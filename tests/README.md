# Kagi MCP Tests

This directory contains comprehensive pytest tests for the Kagi MCP (Model Context Protocol) project.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and configuration
├── test_kagi_api.py         # Tests for KagiAPI class
└── test_tools.py            # Tests for MCP tools (kagi_chat, kagi_summarize, kagi_translate)
```

## Test Coverage

The test suite provides **94% code coverage** and includes 48 comprehensive tests covering:

### test_kagi_api.py (30 tests)

Tests for the core `KagiAPI` class:

- **KagiConfig** - Configuration initialization and defaults
- **KagiAPI Initialization** - Instance creation with/without config and cookie
- **Header Building** - HTTP headers with/without thread_id
- **Request Data Building** - Request payload construction for new and continuing conversations
- **JSON Extraction** - Parsing JSON responses from API
- **Text Decoding** - HTML to Markdown conversion
- **Caching Mechanism** - Cache operations and expiration
- **API Requests** - Successful requests, error handling, and network failures

### test_tools.py (18 tests)

Tests for the MCP tools:

- **kagi_chat Tool**
  - Default parameters and model selection
  - New conversation vs. continuing conversation
  - Internet access control
  - Lens ID support
  - Error handling

- **kagi_summarize Tool**
  - Summary types and model selection
  - Prompt building for webpage summarization
  - Error handling

- **kagi_translate Tool**
  - Translation quality levels and model selection
  - Multiple target languages
  - Prompt building for translation
  - Error handling

- **Tool Integration**
  - Global instance management
  - Instance recreation on setting changes

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=kagi --cov-report=term-missing
```

### Run Specific Test File

```bash
pytest tests/test_kagi_api.py
pytest tests/test_tools.py
```

### Run Specific Test Class

```bash
pytest tests/test_kagi_api.py::TestKagiAPICaching
pytest tests/test_tools.py::TestKagiChatTool
```

### Run Specific Test

```bash
pytest tests/test_kagi_api.py::TestKagiAPICaching::test_cache_expiration
```

## Test Configuration

The tests use:

- **pytest.ini** - Test discovery patterns and configuration
- **conftest.py** - Shared fixtures including environment mocking
- **Mocking** - Extensive use of `unittest.mock` for isolated unit testing
- **Fixtures** - Reusable test components for clean test code

## Key Testing Strategies

### 1. Environment Mocking

Tests use fixtures to mock the `KAGI_COOKIE` environment variable:

```python
@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {'KAGI_COOKIE': 'test_cookie_value'}):
        yield
```

### 2. API Mocking

HTTP requests are mocked to avoid actual API calls:

```python
@patch('requests.Session.post')
def test_send_request_success(self, mock_post, kagi_api):
    mock_response = Mock()
    mock_response.text = 'new_message.json: {"state": "done", "reply": "Test"}'
    mock_post.return_value = mock_response
    # ... test logic
```

### 3. Global State Management

The global `_KAGI_INSTANCE` is reset before each test to ensure test isolation:

```python
@pytest.fixture(autouse=True)
def reset_global_instance():
    import kagi
    kagi._KAGI_INSTANCE = None
    yield
    kagi._KAGI_INSTANCE = None
```

## Requirements

Install test dependencies:

```bash
pip install -r requirements.txt
```

Test dependencies include:
- pytest>=7.0.0
- pytest-mock>=3.10.0
- pytest-cov>=4.0.0

## Continuous Integration

These tests are designed to run in CI/CD pipelines and provide:

- Fast execution (all tests complete in ~2 seconds)
- Comprehensive coverage (94%)
- Isolated tests (no external dependencies)
- Clear error messages
- Consistent results across environments

## Contributing

When adding new features to the Kagi MCP:

1. Write tests first (TDD approach recommended)
2. Ensure all existing tests pass
3. Maintain or improve code coverage
4. Follow the existing test structure and naming conventions
5. Add docstrings to explain test purposes
