import requests
import json
import html
import re
import os
import html2text
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import Field

# Load environment variables from .env file
load_dotenv()

# System instructions for automatic kagi_chat triggering
AUTO_KAGI_SYSTEM_PROMPT = """
This server provides the kagi_chat tool, a search-focused AI assistant powered by Kagi Assistant.
"""

MCP_HOST = os.environ.get("KAGI_MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.environ.get("KAGI_MCP_PORT", "7001"))

# Create MCP service with instructions for automatic kagi_chat triggering.
# Recent FastMCP versions configure HTTP bind settings on the server instance.
mcp = FastMCP(
    "kagimcp",
    dependencies=["mcp[cli]"],
    instructions=AUTO_KAGI_SYSTEM_PROMPT,
    host=MCP_HOST,
    port=MCP_PORT,
)

@dataclass
class KagiConfig:
    """Kagi API Configuration"""
    url: str = 'https://kagi.com/assistant/prompt'
    user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    timeout: int = 30
    rtt: str = '0'
    model: str = 'ki_quick'
    cookie: str = field(default_factory=lambda: os.environ.get('KAGI_COOKIE', ''))
    internet_access: bool = True    # Whether to allow internet access

class KagiAPI:
    def __init__(self):
        """Initialize the Kagi API client."""
        self.config = KagiConfig()
        self._html2text = self._init_html2text()
        self.thread_id = None
        self.message_id = None
        self.session = requests.Session()

    def reset_conversation(self) -> None:
        """Clear conversation state for a fresh thread."""
        self.thread_id = None
        self.message_id = None

    def _init_html2text(self) -> html2text.HTML2Text:
        """Initialize HTML2Text converter"""
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.body_width = 0
        return h

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers"""
        referer = 'https://kagi.com/assistant'
        if self.thread_id:
            referer = f'https://kagi.com/assistant/{self.thread_id}'
            
        return {
            'sec-ch-ua-platform': 'Windows',
            'Referer': referer,
            'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': self.config.user_agent,
            'Accept': 'application/vnd.kagi.stream',
            'Content-Type': 'application/json',
            'rtt': self.config.rtt,
            'Cookie': self.config.cookie
        }

    def _build_request_data(self, prompt_text: str) -> Dict[str, Any]:
        """Build the request payload."""
        focus = {
            "thread_id": self.thread_id,
            "branch_id": "00000000-0000-4000-0000-000000000000",
            "prompt": prompt_text,
        }
        if self.message_id:
            focus["message_id"] = self.message_id

        return {
            "focus": focus,
            "profile": {
                "id": None,
                "personalizations": True,
                "internet_access": self.config.internet_access,
                "model": self.config.model,
                "lens_id": None,
            }
        }

    def extract_json(self, text: str, marker: str) -> Optional[str]:
        """Extract JSON content from text."""
        marker_pos = text.rfind(marker)
        if marker_pos == -1:
            return None

        last_part = text[marker_pos + len(marker):].strip()
        start = last_part.find("{")
        if start == -1:
            return None

        count = 0
        in_string = False
        escape = False
        json_text = []

        for char in last_part[start:]:
            json_text.append(char)
            if not in_string:
                if char == "{":
                    count += 1
                elif char == "}":
                    count -= 1
                    if count == 0:
                        return "".join(json_text)
            elif char == "\\" and not escape:
                escape = True
                continue
            elif char == '"' and not escape:
                in_string = not in_string
            escape = False

        return None

    def decode_text(self, text: str) -> str:
        """Convert HTML to Markdown format text
        
        Args:
            text: HTML text
            
        Returns:
            Converted Markdown text
        """
        # Only process HTML escape when text contains HTML tags
        if '<' in text and '>' in text:
            text = html.unescape(text)
            markdown = self._html2text.handle(text)
            return self._clean_whitespace(markdown)
        return text.strip()
        
    # Pre-compile regex for better performance
    _whitespace_pattern = re.compile(r'\n\s*\n')
    def _clean_whitespace(self, text: str) -> str:
        """Clean extra whitespace lines in text"""
        return self._whitespace_pattern.sub('\n\n', text).strip()

    def send_request(self, prompt_text: str) -> Optional[str]:
        """Send a prompt to Kagi API."""
        if not self.config.cookie:
            return "Error: KAGI_COOKIE environment variable not set. Please set it before running."

        try:
            headers = self._build_headers()
            response = self.session.post(
                self.config.url,
                headers=headers,
                json=self._build_request_data(prompt_text),
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            response.encoding = "utf-8"

            thread_json = self.extract_json(response.text, "thread.json:")
            if thread_json:
                thread_data = json.loads(thread_json)
                if thread_data.get("id"):
                    self.thread_id = thread_data["id"]

            message_json = self.extract_json(response.text, "new_message.json:")
            if message_json:
                message_data = json.loads(message_json)
                if message_data.get("id"):
                    self.message_id = message_data["id"]
                if message_data.get("state") == "done" and message_data.get("reply"):
                    return self.decode_text(message_data["reply"])

            return "Failed to parse response content"
            
        except requests.exceptions.RequestException as e:
            return f"Request error: {e}"

# Global singleton instance
_KAGI_INSTANCE = None


def _get_kagi_instance() -> KagiAPI:
    """Create the singleton client lazily."""
    global _KAGI_INSTANCE
    if _KAGI_INSTANCE is None:
        _KAGI_INSTANCE = KagiAPI()
    return _KAGI_INSTANCE

@mcp.tool()
def kagi_chat(
    prompt: str = Field(
        description="The user's question or instruction to send to Kagi.",
        examples=["What is Bun and does it have compatibility issues?", "Explain this Python traceback."]
    ),
    new_conversation: bool = Field(
        description="Whether to start a new conversation, default is False to continue current conversation",
        default=False
    )
) -> str:
    """Ask Kagi Assistant with the quick model."""
    kagi = _get_kagi_instance()

    if new_conversation:
        kagi.reset_conversation()

    return kagi.send_request(prompt) or (
        "Request failed. Please check your network connection or KAGI_COOKIE environment variable."
    )


if __name__ == "__main__":
    if not KagiConfig().cookie:
        print("Error: KAGI_COOKIE environment variable is not set. Please set it before running.")
        raise SystemExit("KAGI_COOKIE is not set. Service will not start.")

    # Start MCP service with streamable HTTP transport.
    print(f"Starting Kagi MCP service on http://{MCP_HOST}:{MCP_PORT}/mcp")
    mcp.run(transport="streamable-http")
