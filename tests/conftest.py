"""Shared pytest fixtures and configuration"""
import pytest
import os
from unittest.mock import patch


@pytest.fixture(autouse=True)
def reset_global_instance():
    """Reset the global KAGI_INSTANCE before each test"""
    import kagi
    kagi._KAGI_INSTANCE = None
    yield
    kagi._KAGI_INSTANCE = None


@pytest.fixture
def mock_env_cookie():
    """Provide a mock KAGI_COOKIE environment variable"""
    with patch.dict(os.environ, {'KAGI_COOKIE': 'test_cookie_12345'}):
        yield


@pytest.fixture
def clean_env():
    """Provide a clean environment without KAGI_COOKIE"""
    original = os.environ.get('KAGI_COOKIE')
    if 'KAGI_COOKIE' in os.environ:
        del os.environ['KAGI_COOKIE']
    yield
    if original:
        os.environ['KAGI_COOKIE'] = original
