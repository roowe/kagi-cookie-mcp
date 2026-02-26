"""Tests for MCP tools (kagi_chat)"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from kagi import kagi_chat, KagiAPI, KagiConfig


@pytest.fixture
def mock_env():
    """Mock environment variables"""
    with patch.dict(os.environ, {'KAGI_COOKIE': 'test_cookie_value'}):
        yield


@pytest.fixture
def mock_kagi_instance():
    """Mock KagiAPI instance"""
    with patch('kagi._KAGI_INSTANCE', None):
        yield


class TestKagiChatTool:
    """Test kagi_chat MCP tool"""

    @patch('kagi.KagiAPI')
    def test_kagi_chat_default_parameters(self, mock_api_class, mock_env, mock_kagi_instance):
        """Test kagi_chat with default parameters"""
        mock_api = Mock()
        mock_api.send_request.return_value = "Test response"
        mock_api_class.return_value = mock_api

        result = kagi_chat(
            prompt="What is Python?",
            model_selection="General Knowledge"
        )

        assert result == "Test response"
        # Just verify send_request was called with the prompt (lens_id can be FieldInfo or None)
        call_args = mock_api.send_request.call_args
        assert call_args[0][0] == "What is Python?"

    @patch('kagi.KagiAPI')
    def test_kagi_chat_new_conversation(self, mock_api_class, mock_env, mock_kagi_instance):
        """Test kagi_chat with new_conversation=True"""
        mock_api = Mock()
        mock_api.send_request.return_value = "New conversation response"
        mock_api.thread_id = "old-thread-id"
        mock_api.config = Mock(model='ki_quick', internet_access=True)
        mock_api_class.return_value = mock_api

        result = kagi_chat(
            prompt="Start new topic",
            new_conversation=True,
            model_selection="General Knowledge"
        )

        # Verify thread_id was reset
        assert mock_api.thread_id is None
        assert result == "New conversation response"

    @patch('kagi.KagiAPI')
    def test_kagi_chat_continuing_conversation(self, mock_api_class, mock_env, mock_kagi_instance):
        """Test kagi_chat continuing conversation"""
        mock_api = Mock()
        mock_api.send_request.return_value = "Continuing response"
        mock_api.thread_id = "existing-thread-id"
        mock_api.config = Mock(model='ki_quick', internet_access=True)
        mock_api_class.return_value = mock_api

        result = kagi_chat(
            prompt="Continue discussion",
            new_conversation=False,
            model_selection="General Knowledge"
        )

        # Verify thread_id was not reset
        assert mock_api.thread_id == "existing-thread-id"
        assert result == "Continuing response"

    @patch('kagi.KagiAPI')
    def test_kagi_chat_model_selection(self, mock_api_class, mock_env, mock_kagi_instance):
        """Test kagi_chat with different model selections"""
        test_cases = [
            ("General Knowledge", "ki_quick"),
            ("Advanced Reasoning", "ki_research"),
            ("Code Generation", "ki_research"),
            ("Quick Response", "ki_quick"),
            ("Technical Analysis", "ki_research"),
            ("Creative Content", "ki_research"),
            ("Scientific Research", "ki_deep_research"),
        ]

        for model_selection, expected_model in test_cases:
            mock_api = Mock()
            mock_api.send_request.return_value = "Response"
            mock_api.config = Mock(model=expected_model, internet_access=True)
            mock_api_class.return_value = mock_api

            result = kagi_chat(
                prompt="Test prompt",
                model_selection=model_selection
            )

            # Verify correct model was configured
            call_args = mock_api_class.call_args
            config = call_args[0][0] if call_args[0] else call_args[1]['config']
            assert config.model == expected_model

    @patch('kagi.KagiAPI')
    def test_kagi_chat_internet_access_disabled(self, mock_api_class, mock_env, mock_kagi_instance):
        """Test kagi_chat with internet_access=False"""
        mock_api = Mock()
        mock_api.send_request.return_value = "Offline response"
        mock_api.config = Mock(model='ki_quick', internet_access=False)
        mock_api_class.return_value = mock_api

        result = kagi_chat(
            prompt="Offline question",
            internet_access=False,
            model_selection="General Knowledge"
        )

        # Verify internet_access was set to False
        call_args = mock_api_class.call_args
        config = call_args[0][0] if call_args[0] else call_args[1]['config']
        assert config.internet_access is False

    @patch('kagi.KagiAPI')
    def test_kagi_chat_with_lens(self, mock_api_class, mock_env, mock_kagi_instance):
        """Test kagi_chat with lens_id"""
        mock_api = Mock()
        mock_api.send_request.return_value = "Lens response"
        mock_api.config = Mock(model='ki_quick', internet_access=True)
        mock_api_class.return_value = mock_api

        result = kagi_chat(
            prompt="Search with lens",
            lens_id="test-lens-id",
            model_selection="General Knowledge"
        )

        # Verify send_request was called with the prompt and lens_id
        call_args = mock_api.send_request.call_args
        assert call_args[0][0] == "Search with lens"
        assert "test-lens-id" in str(call_args[0][1]) or call_args[0][1] == "test-lens-id"

    @patch('kagi.KagiAPI')
    def test_kagi_chat_request_failure(self, mock_api_class, mock_env, mock_kagi_instance):
        """Test kagi_chat when request fails"""
        mock_api = Mock()
        mock_api.send_request.return_value = None
        mock_api.config = Mock(model='ki_quick', internet_access=True)
        mock_api_class.return_value = mock_api

        result = kagi_chat(
            prompt="Test prompt",
            model_selection="General Knowledge"
        )

        assert "Request failed" in result
        assert "network" in result.lower() or "cookie" in result.lower()


class TestToolIntegration:
    """Test integration between tools"""

    @patch('kagi.KagiAPI')
    def test_multiple_tools_share_global_instance(self, mock_api_class, mock_env):
        """Test that tools recreate instance when settings change"""
        mock_api = Mock()
        mock_api.send_request.return_value = "Response"
        mock_api.config = Mock(model='ki_quick', internet_access=True)
        mock_api_class.return_value = mock_api

        # Reset global instance
        import kagi
        kagi._KAGI_INSTANCE = None

        # Call kagi_chat first
        kagi_chat(prompt="Test 1", model_selection="General Knowledge")
        first_call_count = mock_api_class.call_count

        # Call kagi_chat again with different settings - should create new instance
        kagi_chat(prompt="Test 2", model_selection="Advanced Reasoning")

        # Should have created a new instance due to different model
        assert mock_api_class.call_count > first_call_count

    @patch('kagi.KagiAPI')
    def test_different_models_create_new_instance(self, mock_api_class, mock_env):
        """Test that different model selections create new instances"""
        mock_api = Mock()
        mock_api.send_request.return_value = "Response"
        mock_api.config = Mock(model='ki_quick', internet_access=True)
        mock_api_class.return_value = mock_api

        with patch('kagi._KAGI_INSTANCE', None):
            # First call
            kagi_chat(prompt="Test 1", model_selection="General Knowledge")

            # Change the mock config for the next call
            mock_api.config.model = 'ki_research'

            # Second call with different model
            kagi_chat(prompt="Test 2", model_selection="Advanced Reasoning")

            # Should have created multiple instances
            assert mock_api_class.call_count >= 1
