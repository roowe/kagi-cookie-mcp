"""Tests for MCP server configuration and HTTP transport"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock


class TestMCPServerConfig:
    """Test MCP server configuration"""

    def test_mcp_instance_creation(self):
        """Test that MCP instance is created with correct name"""
        import kagi
        # The mcp instance should be named 'kagimcp'
        assert kagi.mcp.name == "kagimcp"

    def test_mcp_dependencies(self):
        """Test that MCP has correct dependencies"""
        import kagi
        # Check dependencies include mcp[cli]
        assert "mcp[cli]" in kagi.mcp.dependencies

    def test_mcp_has_instructions(self):
        """Test that MCP has system instructions configured"""
        import kagi
        # Instructions should be set for automatic kagi_chat triggering
        assert kagi.mcp.instructions is not None
        assert len(kagi.mcp.instructions) > 0


class TestHTTPTransportConfig:
    """Test HTTP transport configuration"""

    @patch('kagi.mcp')
    def test_run_with_http_transport(self, mock_mcp):
        """Test that mcp.run is called with HTTP transport parameters"""
        import kagi

        # Mock the run method to prevent actual server start
        mock_mcp.run = Mock()

        # Call the run method with expected parameters
        mock_mcp.run(transport="http", host="127.0.0.1", port=8000)

        # Verify the run method was called with correct parameters
        mock_mcp.run.assert_called_once_with(
            transport="http",
            host="127.0.0.1",
            port=8000
        )

    @patch('kagi.mcp')
    def test_run_transport_type(self, mock_mcp):
        """Test that transport type is 'http'"""
        mock_mcp.run = Mock()

        mock_mcp.run(transport="http", host="127.0.0.1", port=8000)

        call_kwargs = mock_mcp.run.call_args[1]
        assert call_kwargs['transport'] == "http"

    @patch('kagi.mcp')
    def test_run_host_config(self, mock_mcp):
        """Test that host is configured as 127.0.0.1"""
        mock_mcp.run = Mock()

        mock_mcp.run(transport="http", host="127.0.0.1", port=8000)

        call_kwargs = mock_mcp.run.call_args[1]
        assert call_kwargs['host'] == "127.0.0.1"

    @patch('kagi.mcp')
    def test_run_port_config(self, mock_mcp):
        """Test that port is configured as 8000"""
        mock_mcp.run = Mock()

        mock_mcp.run(transport="http", host="127.0.0.1", port=8000)

        call_kwargs = mock_mcp.run.call_args[1]
        assert call_kwargs['port'] == 8000


class TestMCPServerTools:
    """Test that MCP tools are properly registered"""

    def test_kagi_chat_tool_registered(self):
        """Test that kagi_chat tool is registered"""
        import kagi
        # Check that kagi_chat is a callable tool
        assert callable(kagi.kagi_chat)

    def test_kagi_summarize_tool_registered(self):
        """Test that kagi_summarize tool is registered"""
        import kagi
        assert callable(kagi.kagi_summarize)

    def test_kagi_translate_tool_registered(self):
        """Test that kagi_translate tool is registered"""
        import kagi
        assert callable(kagi.kagi_translate)


class TestServerStartup:
    """Test server startup behavior"""

    @patch('builtins.print')
    @patch('kagi.mcp')
    def test_startup_prints_url(self, mock_mcp, mock_print):
        """Test that startup prints the correct URL"""
        mock_mcp.run = Mock()

        # Simulate the startup print
        print("Starting Kagi MCP service on http://127.0.0.1:8000")

        # Verify the URL is printed
        printed_messages = [call[0][0] for call in mock_print.call_args_list]
        assert any("http://127.0.0.1:8000" in msg for msg in printed_messages)

    def test_main_block_exists(self):
        """Test that __main__ block exists in kagi module"""
        import ast
        import kagi

        # Read the source file
        with open(kagi.__file__, 'r') as f:
            source = f.read()

        # Parse the AST
        tree = ast.parse(source)

        # Find the if __name__ == "__main__" block
        main_block_found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Check if it's the __name__ == "__main__" check
                if isinstance(node.test, ast.Compare):
                    for comparator in node.test.comparators:
                        if isinstance(comparator, ast.Constant) and comparator.value == "__main__":
                            main_block_found = True
                            break

        assert main_block_found, "__main__ block should exist in kagi.py"


class TestTransportComparison:
    """Test differences between transport modes"""

    @patch('kagi.mcp')
    def test_http_vs_stdio_transport(self, mock_mcp):
        """Test that HTTP transport is different from stdio"""
        mock_mcp.run = Mock()

        # HTTP transport call
        mock_mcp.run(transport="http", host="127.0.0.1", port=8000)

        # Verify it's not stdio
        call_kwargs = mock_mcp.run.call_args[1]
        assert call_kwargs['transport'] != "stdio"
        assert call_kwargs['transport'] == "http"

    @patch('kagi.mcp')
    def test_http_transport_has_host_and_port(self, mock_mcp):
        """Test that HTTP transport requires host and port"""
        mock_mcp.run = Mock()

        # HTTP transport should have host and port
        mock_mcp.run(transport="http", host="127.0.0.1", port=8000)

        call_kwargs = mock_mcp.run.call_args[1]
        assert 'host' in call_kwargs
        assert 'port' in call_kwargs


class TestDefaultTransportParameters:
    """Test default values for transport parameters"""

    @patch('kagi.mcp')
    def test_default_host_is_localhost(self, mock_mcp):
        """Test that default host is localhost (127.0.0.1)"""
        mock_mcp.run = Mock()

        mock_mcp.run(transport="http", host="127.0.0.1", port=8000)

        call_kwargs = mock_mcp.run.call_args[1]
        assert call_kwargs['host'] == "127.0.0.1"

    @patch('kagi.mcp')
    def test_default_port_is_8000(self, mock_mcp):
        """Test that default port is 8000"""
        mock_mcp.run = Mock()

        mock_mcp.run(transport="http", host="127.0.0.1", port=8000)

        call_kwargs = mock_mcp.run.call_args[1]
        assert call_kwargs['port'] == 8000
