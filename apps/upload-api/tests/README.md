# Upload API Tests

This directory contains unit and integration tests for the MedScribe Upload API using Pytest following TDD best practices.

## Test Structure

### Unit Tests

- **test_schemas.py** - Tests for Pydantic models (`UploadResponse`, `HealthResponse`)
- **test_settings.py** - Tests for application settings and configuration
- **test_s3_client.py** - Tests for S3 client with mocked boto3
- **test_db_client.py** - Tests for database client with mocked asyncpg
- **test_mq_publisher.py** - Tests for message queue publisher with mocked Celery

### Integration Tests

- **integration/test_main.py** - End-to-end tests for FastAPI endpoints

## Prerequisites

Before running tests, ensure you have Python 3.12+ installed and all dependencies:

```bash
# Install all dependencies (including test dependencies)
cd apps/upload-api
pip install -r requirements.txt
```

Or install only test dependencies:

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx
```

## Running Tests

### Quick Start

Run all tests:

```bash
cd apps/upload-api
pytest
```

### Basic Commands

#### Run All Tests

```bash
# From the upload-api directory
pytest

# Or from the project root
pytest apps/upload-api/tests/
```

#### Run with Verbose Output

```bash
pytest -v
```

#### Run with Coverage Report

```bash
# Terminal report
pytest --cov=src --cov-report=term

# HTML report (opens in browser)
pytest --cov=src --cov-report=html
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows
```

#### Run Only Unit Tests

```bash
pytest -m "not integration"
```

#### Run Only Integration Tests

```bash
pytest -m integration
```

#### Run Specific Test File

```bash
pytest tests/test_schemas.py
```

#### Run Specific Test Class

```bash
pytest tests/test_schemas.py::TestUploadResponse
```

#### Run Specific Test Method

```bash
pytest tests/test_schemas.py::TestUploadResponse::test_upload_response_should_have_required_fields
```

#### Run Tests Matching a Pattern

```bash
# Run all tests with "schema" in the name
pytest -k schema

# Run all tests with "upload" in the name
pytest -k upload
```

#### Stop on First Failure

```bash
pytest -x
```

#### Show Print Statements

```bash
pytest -s
```

#### Run Tests in Parallel (requires pytest-xdist)

```bash
pip install pytest-xdist
pytest -n auto  # Uses all available CPUs
pytest -n 4     # Uses 4 workers
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (require external services)
- `@pytest.mark.slow` - Slow running tests

## Test Dependencies

The following packages are required for testing (included in `requirements.txt`):

- **pytest** (9.0.0) - Testing framework
- **pytest-asyncio** (1.3.0) - Async test support
- **pytest-cov** (7.0.0) - Code coverage
- **pytest-mock** (3.12.0) - Mocking utilities
- **httpx** (0.28.1) - HTTP client for testing FastAPI

## Environment Variables

Tests use mocked settings via the `mock_settings` fixture in `conftest.py`. The following environment variables are automatically set for testing:

- `S3_ENDPOINT` - S3 endpoint URL
- `S3_BUCKET` - S3 bucket name
- `S3_ACCESS_KEY` - S3 access key
- `S3_SECRET_KEY` - S3 secret key
- `RABBITMQ_URI` - RabbitMQ connection URI
- `DATABASE_URL` - PostgreSQL connection string

**Note:** These are automatically configured by the test fixtures. You don't need to set them manually for running tests.

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `mock_settings` - Mocked application settings
- `sample_pdf_content` - Sample PDF content for testing
- `sample_upload_file` - Mock UploadFile for testing
- `client` - FastAPI TestClient
- `mock_dependencies` - Mocked external dependencies (S3, DB, MQ)

## Test Best Practices

1. **TDD Approach**: Tests are written following Test-Driven Development principles
2. **Arrange-Act-Assert**: All tests follow the AAA pattern
3. **Isolation**: Each test is independent and can run in any order
4. **Mocking**: External dependencies (S3, DB, MQ) are mocked in unit tests
5. **Coverage**: Aim for high code coverage, especially for business logic

## Example Test Structure

```python
class TestFeature:
    """Tests for Feature."""
    
    def test_feature_should_do_something(self):
        """Test that feature does something."""
        # Arrange
        input_data = "test"
        
        # Act
        result = feature.process(input_data)
        
        # Assert
        assert result == "expected"
```

## Integration Tests

Integration tests use mocked dependencies to avoid requiring actual external services:

- S3/Spaces operations are mocked
- Database operations are mocked
- RabbitMQ/Celery operations are mocked

This allows integration tests to run quickly without external dependencies while still testing the full request/response flow.

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError` for modules like `asyncpg`, `boto3`, or `celery`:

```bash
# Install all dependencies
pip install -r requirements.txt
```

### Settings Validation Errors

If tests fail with Pydantic validation errors for Settings, ensure the `mock_settings` fixture is being used (it's set to `autouse=True` in `conftest.py`).

### Async Test Issues

If async tests fail, ensure `pytest-asyncio` is installed:

```bash
pip install pytest-asyncio
```

### Coverage Not Working

If coverage reports are empty, ensure `pytest-cov` is installed:

```bash
pip install pytest-cov
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines without requiring external services. All external dependencies are mocked, making tests fast and reliable.

### Example GitHub Actions Workflow

```yaml
name: Upload API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd apps/upload-api
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd apps/upload-api
          pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./apps/upload-api/coverage.xml
```

## Test Output Examples

### Successful Test Run

```
============================= test session starts =============================
platform win32 -- Python 3.12.7, pytest-8.0.0
collected 7 items

tests/test_schemas.py::TestUploadResponse::test_upload_response_should_have_required_fields PASSED [ 14%]
tests/test_schemas.py::TestUploadResponse::test_upload_response_should_auto_generate_created_at PASSED [ 28%]
...

======================== 7 passed in 0.22s ========================
```

### With Coverage

```
---------- coverage: platform win32, python 3.12.7 -----------
Name                  Stmts   Miss  Cover   Missing
---------------------------------------------------
src/schemas.py           12      0   100%
src/settings.py          20     20     0%   2-38
...
---------------------------------------------------
TOTAL                   158    146     8%
```

