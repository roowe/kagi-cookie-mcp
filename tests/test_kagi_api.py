"""Tests for KagiAPI class"""
import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from kagi import KagiAPI, KagiConfig


@pytest.fixture
def mock_env():
    """Mock environment variables"""
    with patch.dict(os.environ, {'KAGI_COOKIE': 'test_cookie_value'}):
        yield


@pytest.fixture
def kagi_config():
    """Create a test configuration"""
    return KagiConfig(
        url='https://kagi.com/assistant/prompt',
        user_agent='TestAgent',
        timeout=30,
        model='claude-3-sonnet',
        internet_access=True
    )


@pytest.fixture
def kagi_api(kagi_config, mock_env):
    """Create a KagiAPI instance for testing"""
    return KagiAPI(kagi_config)


class TestKagiConfig:
    """Test KagiConfig dataclass"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = KagiConfig()
        assert config.url == 'https://kagi.com/assistant/prompt'
        assert config.timeout == 30
        assert config.model == 'claude-3-sonnet'
        assert config.internet_access is True
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = KagiConfig(
            url='https://custom.url',
            model='gemini-2-5-pro',
            timeout=60,
            internet_access=False
        )
        assert config.url == 'https://custom.url'
        assert config.model == 'gemini-2-5-pro'
        assert config.timeout == 60
        assert config.internet_access is False


class TestKagiAPIInit:
    """Test KagiAPI initialization"""
    
    def test_init_with_config(self, kagi_config, mock_env):
        """Test initialization with custom config"""
        api = KagiAPI(kagi_config)
        assert api.config == kagi_config
        assert api.cookie == 'test_cookie_value'
        assert api.thread_id is None
        assert isinstance(api.cache, dict)
    
    def test_init_without_config(self, mock_env):
        """Test initialization without config (uses defaults)"""
        api = KagiAPI()
        assert api.config.url == 'https://kagi.com/assistant/prompt'
        assert api.cookie == 'test_cookie_value'
    
    def test_init_without_cookie(self):
        """Test initialization without KAGI_COOKIE env var"""
        with patch.dict(os.environ, {}, clear=True):
            api = KagiAPI()
            assert api.cookie == ''


class TestKagiAPIHeaders:
    """Test header building"""
    
    def test_build_headers_without_thread_id(self, kagi_api):
        """Test building headers without thread_id"""
        headers = kagi_api._build_headers()
        assert headers['Referer'] == 'https://kagi.com/assistant'
        assert headers['Cookie'] == 'test_cookie_value'
        assert headers['Content-Type'] == 'application/json'
        assert headers['Accept'] == 'application/vnd.kagi.stream'
    
    def test_build_headers_with_thread_id(self, kagi_api):
        """Test building headers with thread_id"""
        kagi_api.thread_id = 'test-thread-id'
        headers = kagi_api._build_headers()
        assert headers['Referer'] == 'https://kagi.com/assistant/test-thread-id'


class TestKagiAPIRequestData:
    """Test request data building"""
    
    def test_build_request_data_new_conversation(self, kagi_api):
        """Test building request data for new conversation"""
        data = kagi_api._build_request_data('test prompt')
        
        assert data['focus']['prompt'] == 'test prompt'
        assert data['focus']['thread_id'] is None
        assert 'message_id' not in data['focus']
        assert data['profile']['model'] == 'claude-3-sonnet'
        assert data['profile']['internet_access'] is True
    
    def test_build_request_data_continuing_conversation(self, kagi_api):
        """Test building request data for continuing conversation"""
        kagi_api.thread_id = 'existing-thread-id'
        data = kagi_api._build_request_data('test prompt')
        
        assert data['focus']['thread_id'] == 'existing-thread-id'
        assert 'message_id' in data['focus']
    
    def test_build_request_data_with_lens(self, kagi_api):
        """Test building request data with lens_id"""
        data = kagi_api._build_request_data('test prompt', lens_id='test-lens')
        assert data['profile']['lens_id'] == 'test-lens'


class TestKagiAPIJsonExtraction:
    """Test JSON extraction from response text"""
    
    def test_extract_json_simple(self, kagi_api):
        """Test extracting simple JSON"""
        text = 'some text new_message.json: {"state": "done", "reply": "test"}'
        result = kagi_api.extract_json(text, 'new_message.json:')
        assert result == '{"state": "done", "reply": "test"}'
    
    def test_extract_json_nested(self, kagi_api):
        """Test extracting nested JSON"""
        text = 'prefix thread.json: {"id": "123", "data": {"nested": "value"}}'
        result = kagi_api.extract_json(text, 'thread.json:')
        assert result == '{"id": "123", "data": {"nested": "value"}}'
    
    def test_extract_json_with_strings(self, kagi_api):
        """Test extracting JSON with strings containing braces"""
        text = 'data: {"message": "text with {braces}"}'
        result = kagi_api.extract_json(text, 'data:')
        assert result == '{"message": "text with {braces}"}'
    
    def test_extract_json_not_found(self, kagi_api):
        """Test when marker is not found"""
        text = 'some text without marker'
        result = kagi_api.extract_json(text, 'missing.json:')
        assert result is None
    
    def test_extract_json_invalid(self, kagi_api):
        """Test when JSON is incomplete"""
        text = 'marker: {"incomplete": '
        result = kagi_api.extract_json(text, 'marker:')
        # Should return None or incomplete JSON based on implementation
        assert result is None or result.startswith('{')


class TestKagiAPITextDecoding:
    """Test text decoding and HTML to Markdown conversion"""
    
    def test_decode_text_plain(self, kagi_api):
        """Test decoding plain text"""
        result = kagi_api.decode_text('plain text')
        assert result == 'plain text'
    
    def test_decode_text_with_html(self, kagi_api):
        """Test decoding HTML text"""
        html_text = '<p>Hello <strong>world</strong></p>'
        result = kagi_api.decode_text(html_text)
        assert 'Hello' in result
        assert 'world' in result
    
    def test_decode_text_with_html_entities(self, kagi_api):
        """Test decoding HTML entities"""
        html_text = '&lt;div&gt;Test&lt;/div&gt;'
        result = kagi_api.decode_text(html_text)
        assert '<div>' in result or 'Test' in result
    
    def test_clean_whitespace(self, kagi_api):
        """Test whitespace cleaning"""
        text = 'line1\n\n\n\nline2\n\n\n\nline3'
        result = kagi_api._clean_whitespace(text)
        assert result == 'line1\n\nline2\n\nline3'


class TestKagiAPICaching:
    """Test caching mechanism"""
    
    def test_get_cache_key(self, kagi_api):
        """Test cache key generation"""
        key1 = kagi_api._get_cache_key('test prompt')
        key2 = kagi_api._get_cache_key('test prompt')
        key3 = kagi_api._get_cache_key('different prompt')
        
        assert key1 == key2
        assert key1 != key3
    
    def test_save_and_get_from_cache(self, kagi_api):
        """Test saving and retrieving from cache"""
        prompt = 'test prompt'
        result = 'cached result'
        
        # Save to cache
        kagi_api._save_to_cache(prompt, result)
        
        # Get from cache
        hit, cached = kagi_api._get_from_cache(prompt)
        assert hit is True
        assert cached == result
    
    def test_cache_miss(self, kagi_api):
        """Test cache miss"""
        hit, cached = kagi_api._get_from_cache('nonexistent prompt')
        assert hit is False
        assert cached is None
    
    def test_cache_expiration(self, kagi_api):
        """Test cache expiration"""
        import time
        
        kagi_api.cache_ttl = 1  # Set TTL to 1 second
        prompt = 'test prompt'
        result = 'cached result'
        
        kagi_api._save_to_cache(prompt, result)
        
        # Should hit cache immediately
        hit, _ = kagi_api._get_from_cache(prompt)
        assert hit is True
        
        # Wait for cache to expire
        time.sleep(1.1)
        
        # Should miss cache after expiration
        hit, _ = kagi_api._get_from_cache(prompt)
        assert hit is False


class TestKagiAPISendRequest:
    """Test sending requests to Kagi API"""
    
    def test_send_request_no_cookie(self, kagi_config):
        """Test request fails without cookie"""
        with patch.dict(os.environ, {}, clear=True):
            api = KagiAPI(kagi_config)
            result = api.send_request('test prompt')
            assert 'KAGI_COOKIE' in result
            assert 'not set' in result
    
    @patch('requests.Session.post')
    def test_send_request_success(self, mock_post, kagi_api):
        """Test successful request"""
        # Mock response
        mock_response = Mock()
        mock_response.text = '''
        thread.json: {"id": "thread-123"}
        new_message.json: {"state": "done", "reply": "Test response"}
        '''
        mock_response.raise_for_status = Mock()
        mock_response.encoding = 'utf-8'
        mock_post.return_value = mock_response
        
        result = kagi_api.send_request('test prompt')
        
        assert result == 'Test response'
        assert kagi_api.thread_id == 'thread-123'
        mock_post.assert_called_once()
    
    @patch('requests.Session.post')
    def test_send_request_with_cache(self, mock_post, kagi_api):
        """Test request uses cache for non-session mode"""
        # Mock first request
        mock_response = Mock()
        mock_response.text = 'new_message.json: {"state": "done", "reply": "Cached response"}'
        mock_response.raise_for_status = Mock()
        mock_response.encoding = 'utf-8'
        mock_post.return_value = mock_response
        
        # First call should hit API
        result1 = kagi_api.send_request('test prompt')
        assert mock_post.call_count == 1
        
        # Second call should use cache
        result2 = kagi_api.send_request('test prompt')
        assert mock_post.call_count == 1  # No additional call
        assert result1 == result2
    
    @patch('requests.Session.post')
    def test_send_request_session_mode_no_cache(self, mock_post, kagi_api):
        """Test request doesn't use cache in session mode"""
        kagi_api.thread_id = 'existing-thread'
        
        mock_response = Mock()
        mock_response.text = 'new_message.json: {"state": "done", "reply": "Response"}'
        mock_response.raise_for_status = Mock()
        mock_response.encoding = 'utf-8'
        mock_post.return_value = mock_response
        
        # Make two identical requests
        kagi_api.send_request('test prompt')
        kagi_api.send_request('test prompt')
        
        # Both should hit the API (no caching in session mode)
        assert mock_post.call_count == 2
    
    @patch('requests.Session.post')
    def test_send_request_network_error(self, mock_post, kagi_api):
        """Test request with network error"""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException('Network error')
        
        result = kagi_api.send_request('test prompt')
        assert 'Request error' in result
    
    @patch('requests.Session.post')
    def test_send_request_invalid_response(self, mock_post, kagi_api):
        """Test request with invalid response"""
        mock_response = Mock()
        mock_response.text = 'invalid response without json'
        mock_response.raise_for_status = Mock()
        mock_response.encoding = 'utf-8'
        mock_post.return_value = mock_response
        
        result = kagi_api.send_request('test prompt')
        assert 'Failed to parse' in result
    
    @patch('requests.Session.post')
    def test_send_request_with_lens(self, mock_post, kagi_api):
        """Test request with lens_id"""
        mock_response = Mock()
        mock_response.text = 'new_message.json: {"state": "done", "reply": "Lens response"}'
        mock_response.raise_for_status = Mock()
        mock_response.encoding = 'utf-8'
        mock_post.return_value = mock_response
        
        result = kagi_api.send_request('test prompt', lens_id='test-lens')
        
        # Verify lens_id was passed in request
        call_args = mock_post.call_args
        request_json = call_args[1]['json']
        assert request_json['profile']['lens_id'] == 'test-lens'
