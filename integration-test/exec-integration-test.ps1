# MedScribe Integration Test Script (PowerShell)
# This script runs a complete integration test of the MedScribe system

$ErrorActionPreference = "Stop"

# Configuration
$COMPOSE_FILE = "../localhost/docker-compose.yaml"
$PDF_FILE = "./file-to-upload/laudo.pdf"
$UPLOAD_API_URL = "http://localhost:8000"
$DATA_API_URL = "http://localhost:8001"
$DB_CONTAINER = "medscribe-postgres"
$DB_USER = "medscribe"
$DB_PASSWORD = "medscribe123"
$DB_NAME = "medscribe"
$MAX_WAIT = 120

# Test results
$script:TESTS_PASSED = 0
$script:TESTS_FAILED = 0
$script:TEST_RESULTS = @()
$script:TEST_START_TIME = Get-Date

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
    $script:TESTS_PASSED++
    $script:TEST_RESULTS += "✅ $Message"
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    $script:TESTS_FAILED++
    $script:TEST_RESULTS += "❌ $Message"
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Wait-ForService {
    param(
        [string]$ServiceName,
        [string]$Url,
        [int]$MaxAttempts = 30
    )
    
    Write-Info "Waiting for $ServiceName to be ready..."
    
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "$ServiceName is ready"
                return $true
            }
        } catch {
            # Service not ready yet
        }
        Start-Sleep -Seconds 2
    }
    
    Write-Error "$ServiceName failed to start after $MaxAttempts attempts"
    return $false
}

function Wait-ForLog {
    param(
        [string]$Service,
        [string]$Pattern,
        [int]$MaxAttempts = 30
    )
    
    Write-Info "Waiting for log pattern '$Pattern' in $Service..."
    
    $composeDir = Split-Path -Parent $COMPOSE_FILE
    $composeFile = Split-Path -Leaf $COMPOSE_FILE
    
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        Push-Location $composeDir
        try {
            $logs = docker compose -f $composeFile logs $Service 2>&1
            if ($logs -match $Pattern) {
                Write-Success "Found log pattern in $Service"
                return $true
            }
        } catch {
            # Continue waiting
        }
        finally {
            Pop-Location
        }
        Start-Sleep -Seconds 2
    }
    
    Write-Warning "Log pattern not found in $Service (may be normal)"
    return $false
}

function Check-DockerCompose {
    # Check for docker compose (v2) or docker-compose (v1)
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        $dockerComposeV2 = docker compose version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $script:DOCKER_COMPOSE_CMD = "docker compose"
            Write-Success "Docker Compose (v2) found"
            return $true
        }
    }
    
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        $script:DOCKER_COMPOSE_CMD = "docker-compose"
        Write-Success "Docker Compose (v1) found"
        return $true
    }
    
    Write-Error "docker-compose not found. Please install Docker Compose."
    exit 1
}

function Invoke-DockerCompose {
    param(
        [string[]]$Arguments
    )
    
    $composeDir = Split-Path -Parent $COMPOSE_FILE
    $composeFile = Split-Path -Leaf $COMPOSE_FILE
    
    Push-Location $composeDir
    try {
        $cmd = "$script:DOCKER_COMPOSE_CMD -f $composeFile " + ($Arguments -join " ")
        Invoke-Expression $cmd
        if ($LASTEXITCODE -ne 0) {
            throw "Docker Compose command failed"
        }
    } finally {
        Pop-Location
    }
}

function Invoke-PostgresQuery {
    param(
        [string]$Query
    )
    
    $fullQuery = "PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -t -c `"$Query`""
    $result = docker exec $DB_CONTAINER sh -c $fullQuery 2>&1
    return $result.Trim()
}

# Main execution
function Main {
    Write-Info "========================================="
    Write-Info "MedScribe Integration Test"
    Write-Info "========================================="
    Write-Host ""
    
    # Step 1: Check prerequisites
    Write-Info "Step 1: Checking prerequisites..."
    Check-DockerCompose
    
    if (-not (Test-Path $PDF_FILE)) {
        Write-Error "PDF file not found: $PDF_FILE"
        exit 1
    }
    Write-Success "PDF file found: $PDF_FILE"
    Write-Host ""
    
    # Step 2: Start services
    Write-Info "Step 2: Starting Docker Compose services..."
    Invoke-DockerCompose @("down", "-v")
    Start-Sleep -Seconds 2
    Invoke-DockerCompose @("up", "-d")
    
    Write-Info "Waiting for services to initialize..."
    Start-Sleep -Seconds 10
    Write-Host ""
    
    # Step 3: Wait for services to be healthy
    Write-Info "Step 3: Waiting for services to be healthy..."
    Wait-ForService -ServiceName "Upload API" -Url "$UPLOAD_API_URL/healthz" | Out-Null
    Wait-ForService -ServiceName "Data API" -Url "$DATA_API_URL/healthz" | Out-Null
    Write-Host ""
    
    # Step 4: Check initial logs
    Write-Info "Step 4: Checking initial service logs..."
    try {
        $uploadLogs = docker logs medscribe-upload-api 2>&1 | Select-String -Pattern "Application startup|Uvicorn running|started" -Quiet
        $dataLogs = docker logs medscribe-data-api 2>&1 | Select-String -Pattern "Application started|Now listening|started" -Quiet
        
        if ($uploadLogs -or $dataLogs) {
            Write-Success "Services started successfully"
        } else {
            Write-Warning "Could not verify startup logs (may be normal)"
        }
    } catch {
        Write-Warning "Could not check logs (may be normal)"
    }
    Write-Host ""
    
    # Step 5: Upload PDF
    Write-Info "Step 5: Uploading PDF file..."
    
    try {
        # Use curl for multipart form upload (more reliable in PowerShell)
        $pdfPath = Resolve-Path $PDF_FILE
        $curlResponse = & curl.exe -s -w "`n%{http_code}" -X POST "$UPLOAD_API_URL/upload" -F "file=@$pdfPath" 2>&1
        
        $httpCode = ($curlResponse | Select-Object -Last 1).Trim()
        $responseBody = ($curlResponse | Select-Object -SkipLast 1) -join "`n"
        
        if ($httpCode -eq "202") {
            Write-Success "PDF uploaded successfully (HTTP $httpCode)"
            $jsonResponse = $responseBody | ConvertFrom-Json
            $documentId = $jsonResponse.document_id
            Write-Info "Document ID: $documentId"
        } else {
            Write-Error "PDF upload failed (HTTP $httpCode)"
            Write-Host "Response: $responseBody"
            exit 1
        }
    } catch {
        Write-Error "PDF upload failed: $($_.Exception.Message)"
        exit 1
    }
    Write-Host ""
    
    # Step 6: Wait for processing
    Write-Info "Step 6: Waiting for document processing..."
    Start-Sleep -Seconds 5
    
    Wait-ForLog -Service "doc-worker" -Pattern "Processamento concluído|processing completed|DONE" | Out-Null
    Write-Host ""
    
    # Step 7: Check database
    Write-Info "Step 7: Checking database for inserted records..."
    Start-Sleep -Seconds 5
    
    $dbCheck = Invoke-PostgresQuery "SELECT COUNT(*) FROM documents WHERE id = '$documentId' AND status = 'DONE';"
    
    if ($dbCheck -eq "1") {
        Write-Success "Document found in database with status DONE"
        
        $fieldsCount = Invoke-PostgresQuery "SELECT COUNT(*) FROM document_fields WHERE document_id = '$documentId';"
        
        $fieldsCountInt = if ($fieldsCount -is [array]) { $fieldsCount.Count } else { [int]$fieldsCount }
        if ($fieldsCountInt -gt 0) {
            Write-Success "Found $fieldsCount extracted fields in database"
        } else {
            Write-Warning "No fields found in database (may be normal if OCR didn't extract fields)"
        }
    } else {
        Write-Error "Document not found in database or status is not DONE"
        Write-Info "Checking document status..."
        Invoke-PostgresQuery "SELECT id, status, error_message FROM documents WHERE id = '$documentId';" | Out-Host
    }
    Write-Host ""
    
    # Step 8: Query Data API
    Write-Info "Step 8: Querying Data API..."
    
    $docResponse = $null
    $fieldsResponse = $null
    
    # Get document
    try {
        $docResponse = Invoke-RestMethod -Uri "$DATA_API_URL/documents/$documentId" -Method Get -ErrorAction Stop
        Write-Success "Document retrieved from Data API"
        Write-Host "Document data:"
        $docResponse | ConvertTo-Json -Depth 10 | Write-Host
    } catch {
        Write-Error "Failed to retrieve document: $($_.Exception.Message)"
    }
    Write-Host ""
    
    # Get document fields
    try {
        $fieldsResponse = Invoke-RestMethod -Uri "$DATA_API_URL/documents/$documentId/fields" -Method Get -ErrorAction Stop
        $fieldsCount = ($fieldsResponse | Measure-Object).Count
        Write-Success "Document fields retrieved from Data API"
        Write-Info "Fields count from API: $fieldsCount"
        
        if ($fieldsCount -gt 0) {
            Write-Host "Sample fields:"
            $fieldsResponse | Select-Object -First 5 | ConvertTo-Json -Depth 10 | Write-Host
        }
    } catch {
        Write-Warning "Failed to retrieve fields - may be normal if no fields extracted"
    }
    Write-Host ""
    
    # Step 9: Validate results
    Write-Info "Step 9: Validating results..."
    
    if ($docResponse -and $dbCheck -eq "1") {
        Write-Success "Integration test validation passed"
    } else {
        Write-Error "Integration test validation failed"
    }
    Write-Host ""
    
    # Step 10: Cleanup test data
    Write-Info "Step 10: Cleaning up test data..."
    
    Invoke-PostgresQuery "DELETE FROM documents WHERE id = '$documentId';" | Out-Null
    
    $verifyCleanup = Invoke-PostgresQuery "SELECT COUNT(*) FROM documents WHERE id = '$documentId';"
    
    if ($verifyCleanup -eq "0") {
        Write-Success "Test data cleaned up from database"
    } else {
        Write-Warning "Could not verify cleanup (may have already been deleted)"
    }
    Write-Host ""
    
    # Step 11: Generate report
    Write-Info "========================================="
    Write-Info "Integration Test Report"
    Write-Info "========================================="
    Write-Host ""
    Write-Host "Test Results:"
    foreach ($result in $script:TEST_RESULTS) {
        Write-Host "  $result"
    }
    Write-Host ""
    Write-Host "Summary:"
    Write-Host "  ✅ Passed: $($script:TESTS_PASSED)"
    Write-Host "  ❌ Failed: $($script:TESTS_FAILED)"
    Write-Host ""
    
    $TEST_END_TIME = Get-Date
    $TEST_DURATION = ($TEST_END_TIME - $script:TEST_START_TIME).TotalSeconds
    Write-Host "Total duration: $([math]::Round($TEST_DURATION, 2))s"
    Write-Host ""
    
    if ($script:TESTS_FAILED -eq 0) {
        Write-Success "All tests passed!"
        exit 0
    } else {
        Write-Error "Some tests failed"
        exit 1
    }
}

# Run main function
Main

