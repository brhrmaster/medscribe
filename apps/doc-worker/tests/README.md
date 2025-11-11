# Doc Worker Tests

This directory contains the test suite for the `doc-worker` application, following Test-Driven Development (TDD) best practices.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── test_models.py           # Unit tests for Pydantic models
├── test_settings.py         # Unit tests for settings
├── test_pdf_loader.py       # Unit tests for PDF loader (S3)
├── test_rasterizer.py       # Unit tests for PDF rasterization
├── test_preprocess.py       # Unit tests for image preprocessing
├── test_ocr_printed.py      # Unit tests for OCR (printed text)
├── test_htr_handwritten.py  # Unit tests for HTR (handwritten text)
├── test_postprocess.py      # Unit tests for data normalization
├── test_mapping.py          # Unit tests for field extraction
├── test_persistence.py       # Unit tests for database operations
├── integration/
│   ├── __init__.py
│   └── test_worker.py      # Integration tests for Celery worker
└── README.md               # This file
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
# From apps/doc-worker directory
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=term-missing
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Slow tests
pytest -m slow

# OCR-related tests (requires Tesseract)
pytest -m ocr

# ONNX-related tests
pytest -m onnx
```

### Run Specific Test Files

```bash
# Test models only
pytest tests/test_models.py

# Test settings only
pytest tests/test_settings.py

# Test integration tests
pytest tests/integration/
```

### Verbose Output

```bash
pytest -v
```

## Test Categories

### Unit Tests

Fast tests that don't require external dependencies:

- **test_models.py**: Tests for Pydantic models (`BoundingBox`, `DocumentField`, `MedicalReport`)
- **test_settings.py**: Tests for configuration loading
- **test_postprocess.py**: Tests for data normalization functions
- **test_mapping.py**: Tests for field extraction logic

### Unit Tests with Mocks

Tests that mock external dependencies:

- **test_pdf_loader.py**: Tests for S3 PDF download (mocks `boto3`)
- **test_rasterizer.py**: Tests for PDF to image conversion (mocks `PyMuPDF`)
- **test_preprocess.py**: Tests for image preprocessing (uses OpenCV)
- **test_ocr_printed.py**: Tests for OCR (mocks `pytesseract`)
- **test_htr_handwritten.py**: Tests for HTR (mocks ONNX runtime)
- **test_persistence.py**: Tests for database operations (mocks `asyncpg`)

### Integration Tests

Tests that verify the full pipeline:

- **test_worker.py**: Tests for the Celery worker task `process_document`

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `sample_pdf_content`: Minimal valid PDF bytes
- `sample_image`: PIL Image (RGB, 100x100)
- `sample_grayscale_image`: PIL Image (grayscale, 100x100)
- `sample_numpy_array`: NumPy array for testing
- `mock_settings`: Auto-applied fixture that sets test environment variables

## Mocking Strategy

Following the pattern established in `upload-api` tests:

1. **Module Reloading**: Tests that need to mock module-level imports delete and reload modules
2. **Context Managers**: Use `with patch()` context managers instead of `@patch` decorators when modules are reloaded
3. **Async Mocks**: Use `AsyncMock` for async functions, `Mock` for regular functions that return async context managers

Example:

```python
with patch('src.pipeline.persistence.asyncpg', create=True) as mock_asyncpg:
    mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)
    from src.pipeline.persistence import Persistence
    # Test code here
```

## Test Coverage

The test suite aims for high coverage of:

- ✅ All Pydantic models and validation
- ✅ Configuration loading and defaults
- ✅ PDF loading and validation
- ✅ Image preprocessing operations
- ✅ OCR and HTR functions
- ✅ Field extraction and normalization
- ✅ Database persistence operations
- ✅ Worker task orchestration

## Dependencies

Test dependencies (included in `requirements.txt`):

- `pytest>=9.0.0`
- `pytest-asyncio>=1.3.0`
- `pytest-cov>=7.0.0`
- `pytest-mock>=3.12.0`

## Notes

- **OCR Tests**: Some tests mock `pytesseract` to avoid requiring Tesseract installation
- **ONNX Tests**: HTR tests are currently placeholders as ONNX implementation is not complete
- **Integration Tests**: May require actual Celery broker for full integration testing (currently mocked)

## Troubleshooting

### Import Errors

If you see import errors, ensure:
1. Environment variables are set (via `conftest.py` fixtures)
2. Modules are properly reloaded in tests that mock dependencies

### Async Test Failures

Ensure:
1. `pytest-asyncio` is installed
2. Tests are marked with `@pytest.mark.asyncio`
3. `AsyncMock` is used for async functions

### Mock Not Applied

If mocks aren't being applied:
1. Check that modules are deleted before patching
2. Use `with patch()` context managers instead of decorators
3. Ensure patches are applied before module import

