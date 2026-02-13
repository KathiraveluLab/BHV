# BHV Unit Tests

Comprehensive test suite for the Behavioral Health Vault application.

## Test Results

✅ **11 tests passing**

## Running Tests

### Run all tests:
```bash
python -m pytest -v
```

### Run specific test file:
```bash
python -m pytest tests/test_validators.py -v
```

### Run with coverage:
```bash
python -m pytest --cov=bhv
```

## Test Coverage

- **Validators** (5 tests): File validation, sanitization, security
- **Models** (3 tests): User model, password hashing
- **Upload** (3 tests): App creation, routes, health endpoint

## Test Files
```
tests/
├── test_validators.py   # Validation logic tests
├── test_models.py       # Database model tests
├── test_upload.py       # Route and endpoint tests
└── README.md           # This file
```

## Security Tests Included

✅ Path traversal prevention
✅ File extension validation
✅ Password hashing verification
✅ File size validation