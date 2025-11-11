# Integration Tests

This directory contains integration test scripts for the MedScribe system.

## Files

- `exec-integration-test.sh` - Bash script for Linux/Mac
- `exec-integration-test.ps1` - PowerShell script for Windows
- `file-to-upload/laudo.pdf` - Test PDF file for upload

## Prerequisites

- Docker and Docker Compose installed
- `curl` command available (for bash script)
- PowerShell 5.1+ (for PowerShell script)
- Services must be accessible on:
  - Upload API: http://localhost:8000
  - Data API: http://localhost:8001
  - PostgreSQL: localhost:5432

## Usage

### Linux/Mac (Bash)

```bash
cd integration-test
chmod +x exec-integration-test.sh
./exec-integration-test.sh
```

### Windows (PowerShell)

```powershell
cd integration-test
.\exec-integration-test.ps1
```

## What the Scripts Do

1. **Start Services**: Execute docker-compose with the localhost configuration
2. **Wait for Health**: Check and validate that all services are healthy
3. **Check Initial Logs**: Validate service startup logs
4. **Upload PDF**: Upload the test PDF file (`laudo.pdf`) to the Upload API
5. **Wait for Processing**: Monitor worker logs for processing completion
6. **Check Database**: Verify that the document and fields were inserted into PostgreSQL
7. **Query Data API**: Retrieve document and fields via the Data API
8. **Validate Results**: Ensure all operations completed successfully
9. **Cleanup**: Remove test data from the database
10. **Generate Report**: Display test results summary

## Expected Output

The scripts will output:
- ✅ Success messages for each step
- ❌ Error messages if something fails
- Test summary with pass/fail counts
- Total execution time

## Exit Codes

- `0`: All tests passed
- `1`: One or more tests failed

## Troubleshooting

### Services don't start

- Check if ports 5432, 5672, 8000, 8001 are available
- Verify Docker is running
- Check docker-compose logs: `docker-compose -f ../localhost/docker-compose.yaml logs`

### Upload fails

- Verify Upload API is accessible: `curl http://localhost:8000/healthz`
- Check Upload API logs: `docker logs medscribe-upload-api`

### Processing doesn't complete

- Check worker logs: `docker logs medscribe-doc-worker`
- Verify RabbitMQ is running: `curl http://localhost:15672`
- Check if there are messages in the queue

### Database queries fail

- Verify PostgreSQL is running: `docker ps | grep postgres`
- Check connection: `docker exec medscribe-postgres psql -U medscribe -d medscribe -c "SELECT 1;"`

## Notes

- The scripts will clean up Docker volumes on start (`docker-compose down -v`)
- Test data is automatically removed from the database after validation
- The scripts wait up to 60 seconds for processing to complete
- Logs are checked for success patterns but warnings are non-fatal

