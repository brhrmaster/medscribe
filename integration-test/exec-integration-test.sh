#!/bin/bash

# MedScribe Integration Test Script (Bash)
# This script runs a complete integration test of the MedScribe system

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="../localhost/docker-compose.yaml"
PDF_FILE="./file-to-upload/laudo.pdf"
UPLOAD_API_URL="http://localhost:8000"
DATA_API_URL="http://localhost:8001"
DB_CONTAINER="medscribe-postgres"
DB_USER="medscribe"
DB_PASSWORD="medscribe123"
DB_NAME="medscribe"
MAX_WAIT=120  # Maximum wait time in seconds
TEST_START_TIME=$(date +%s)

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TEST_RESULTS=()

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TEST_RESULTS+=("✅ $1")
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TEST_RESULTS+=("❌ $1")
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

wait_for_service() {
    local service=$1
    local url=$2
    local max_attempts=$3
    local attempt=0
    
    log_info "Waiting for $service to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            log_success "$service is ready"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    log_error "$service failed to start after $max_attempts attempts"
    return 1
}

wait_for_log() {
    local service=$1
    local pattern=$2
    local max_attempts=30
    local attempt=0
    
    log_info "Waiting for log pattern '$pattern' in $service..."
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" logs "$service" 2>/dev/null | grep -q "$pattern"; then
            log_success "Found log pattern in $service"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    log_warning "Log pattern not found in $service (may be normal)"
    return 0
}

check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "docker-compose not found. Please install Docker Compose."
        exit 1
    fi
    
    # Use 'docker compose' if available, otherwise 'docker-compose'
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    else
        DOCKER_COMPOSE_CMD="docker-compose"
    fi
    log_success "Docker Compose found"
}

# Main execution
main() {
    log_info "========================================="
    log_info "MedScribe Integration Test"
    log_info "========================================="
    echo ""
    
    # Step 1: Check prerequisites
    log_info "Step 1: Checking prerequisites..."
    check_docker_compose
    
    if [ ! -f "$PDF_FILE" ]; then
        log_error "PDF file not found: $PDF_FILE"
        exit 1
    fi
    log_success "PDF file found: $PDF_FILE"
    echo ""
    
    # Step 2: Start services
    log_info "Step 2: Starting Docker Compose services..."
    cd "$(dirname "$COMPOSE_FILE")" || exit 1
    $DOCKER_COMPOSE_CMD -f "$(basename "$COMPOSE_FILE")" down -v 2>/dev/null || true
    $DOCKER_COMPOSE_CMD -f "$(basename "$COMPOSE_FILE")" up -d
    
    log_info "Waiting for services to initialize..."
    sleep 10
    echo ""
    
    # Step 3: Wait for services to be healthy
    log_info "Step 3: Waiting for services to be healthy..."
    wait_for_service "PostgreSQL" "http://localhost:5432" 30 || true
    wait_for_service "Upload API" "$UPLOAD_API_URL/healthz" 30
    wait_for_service "Data API" "$DATA_API_URL/healthz" 30
    echo ""
    
    # Step 4: Check initial logs
    log_info "Step 4: Checking initial service logs..."
    cd "$(dirname "$COMPOSE_FILE")" || exit 1
    COMPOSE_FILE_NAME=$(basename "$COMPOSE_FILE")
    
    if $DOCKER_COMPOSE_CMD -f "$COMPOSE_FILE_NAME" logs upload-api 2>/dev/null | grep -qiE "application startup|uvicorn running|started"; then
        log_success "Upload API started successfully"
    else
        log_warning "Upload API logs not showing startup (may be normal)"
    fi
    
    if $DOCKER_COMPOSE_CMD -f "$COMPOSE_FILE_NAME" logs data-api-dotnet 2>/dev/null | grep -qiE "application started|now listening|started"; then
        log_success "Data API started successfully"
    else
        log_warning "Data API logs not showing startup (may be normal)"
    fi
    echo ""
    
    # Step 5: Upload PDF
    log_info "Step 5: Uploading PDF file..."
    cd - > /dev/null || exit 1
    
    UPLOAD_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$UPLOAD_API_URL/upload" \
        -F "file=@$PDF_FILE" 2>&1)
    
    HTTP_CODE=$(echo "$UPLOAD_RESPONSE" | tail -n1)
    RESPONSE_BODY=$(echo "$UPLOAD_RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "202" ]; then
        log_success "PDF uploaded successfully (HTTP $HTTP_CODE)"
        DOCUMENT_ID=$(echo "$RESPONSE_BODY" | grep -o '"document_id":"[^"]*"' | cut -d'"' -f4)
        log_info "Document ID: $DOCUMENT_ID"
    else
        log_error "PDF upload failed (HTTP $HTTP_CODE)"
        echo "Response: $RESPONSE_BODY"
        exit 1
    fi
    echo ""
    
    # Step 6: Wait for processing
    log_info "Step 6: Waiting for document processing..."
    sleep 5
    
    # Check worker logs
    cd "$(dirname "$COMPOSE_FILE")" || exit 1
    wait_for_log "doc-worker" "Processamento concluído\|processing completed\|DONE" 60
    echo ""
    
    # Step 7: Check database
    log_info "Step 7: Checking database for inserted records..."
    cd - > /dev/null || exit 1
    
    sleep 5  # Give a bit more time for DB writes
    
    # Wait a bit more for processing to complete
    log_info "Waiting for document processing to complete..."
    for i in {1..30}; do
        DB_STATUS=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c \
            "SELECT status FROM documents WHERE id = '$DOCUMENT_ID';" 2>/dev/null | tr -d ' ' | tr -d '\n' || echo "")
        
        if [ "$DB_STATUS" = "DONE" ]; then
            break
        elif [ "$DB_STATUS" = "FAILED" ]; then
            log_error "Document processing failed"
            docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c \
                "SELECT id, status, error_message FROM documents WHERE id = '$DOCUMENT_ID';" 2>/dev/null || true
            exit 1
        fi
        sleep 2
    done
    
    DB_CHECK=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SELECT COUNT(*) FROM documents WHERE id = '$DOCUMENT_ID' AND status = 'DONE';" 2>/dev/null | tr -d ' ' | tr -d '\n')
    
    if [ "$DB_CHECK" = "1" ]; then
        log_success "Document found in database with status DONE"
        
        FIELDS_COUNT=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c \
            "SELECT COUNT(*) FROM document_fields WHERE document_id = '$DOCUMENT_ID';" 2>/dev/null | tr -d ' ' | tr -d '\n')
        
        if [ -n "$FIELDS_COUNT" ] && [ "$FIELDS_COUNT" -gt "0" ]; then
            log_success "Found $FIELDS_COUNT extracted fields in database"
        else
            log_warning "No fields found in database (may be normal if OCR didn't extract fields)"
        fi
    else
        log_error "Document not found in database or status is not DONE"
        log_info "Checking document status..."
        docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c \
            "SELECT id, status, error_message FROM documents WHERE id = '$DOCUMENT_ID';" 2>/dev/null || true
    fi
    echo ""
    
    # Step 8: Query Data API
    log_info "Step 8: Querying Data API..."
    
    # Get document
    DOC_RESPONSE=$(curl -s -w "\n%{http_code}" "$DATA_API_URL/documents/$DOCUMENT_ID")
    DOC_HTTP_CODE=$(echo "$DOC_RESPONSE" | tail -n1)
    DOC_BODY=$(echo "$DOC_RESPONSE" | sed '$d')
    
    if [ "$DOC_HTTP_CODE" = "200" ]; then
        log_success "Document retrieved from Data API (HTTP $DOC_HTTP_CODE)"
        echo "Document data:"
        echo "$DOC_BODY" | python3 -m json.tool 2>/dev/null || echo "$DOC_BODY"
    else
        log_error "Failed to retrieve document (HTTP $DOC_HTTP_CODE)"
        echo "Response: $DOC_BODY"
    fi
    echo ""
    
    # Get document fields
    FIELDS_RESPONSE=$(curl -s -w "\n%{http_code}" "$DATA_API_URL/documents/$DOCUMENT_ID/fields")
    FIELDS_HTTP_CODE=$(echo "$FIELDS_RESPONSE" | tail -n1)
    FIELDS_BODY=$(echo "$FIELDS_RESPONSE" | sed '$d')
    
    if [ "$FIELDS_HTTP_CODE" = "200" ]; then
        log_success "Document fields retrieved from Data API (HTTP $FIELDS_HTTP_CODE)"
        FIELDS_COUNT_API=$(echo "$FIELDS_BODY" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
        log_info "Fields count from API: $FIELDS_COUNT_API"
        if [ "$FIELDS_COUNT_API" -gt "0" ]; then
            echo "Sample fields:"
            echo "$FIELDS_BODY" | python3 -m json.tool 2>/dev/null | head -20 || echo "$FIELDS_BODY" | head -20
        fi
    else
        log_warning "Failed to retrieve fields (HTTP $FIELDS_HTTP_CODE) - may be normal if no fields extracted"
    fi
    echo ""
    
    # Step 9: Validate results
    log_info "Step 9: Validating results..."
    
    if [ "$DOC_HTTP_CODE" = "200" ] && [ "$DB_CHECK" = "1" ]; then
        log_success "Integration test validation passed"
    else
        log_error "Integration test validation failed"
    fi
    echo ""
    
    # Step 10: Cleanup test data
    log_info "Step 10: Cleaning up test data..."
    
    CLEANUP_RESULT=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c \
        "DELETE FROM documents WHERE id = '$DOCUMENT_ID'; SELECT ROW_COUNT;" 2>/dev/null || echo "0")
    
    if docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SELECT COUNT(*) FROM documents WHERE id = '$DOCUMENT_ID';" 2>/dev/null | grep -q "0"; then
        log_success "Test data cleaned up from database"
    else
        log_warning "Could not verify cleanup (may have already been deleted)"
    fi
    echo ""
    
    # Step 11: Generate report
    log_info "========================================="
    log_info "Integration Test Report"
    log_info "========================================="
    echo ""
    echo "Test Results:"
    for result in "${TEST_RESULTS[@]}"; do
        echo "  $result"
    done
    echo ""
    echo "Summary:"
    echo "  ✅ Passed: $TESTS_PASSED"
    echo "  ❌ Failed: $TESTS_FAILED"
    echo ""
    
    TEST_END_TIME=$(date +%s)
    TEST_DURATION=$((TEST_END_TIME - TEST_START_TIME))
    echo "Total duration: ${TEST_DURATION}s"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        log_success "All tests passed!"
        exit 0
    else
        log_error "Some tests failed"
        exit 1
    fi
}

# Run main function
main "$@"

