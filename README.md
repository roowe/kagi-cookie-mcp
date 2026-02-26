# Kagi MCP - Intelligent Search Assistant

Kagi MCP is an intelligent assistant based on the Model Control Protocol (MCP) that integrates Kagi's AI services to provide high-quality search-driven conversations, webpage summaries, and text translation capabilities. This tool leverages multiple advanced AI models, automatically selecting the most appropriate model for different task types to ensure optimal response quality.

## Features

### 1. Intelligent Conversation (kagi_chat)

Automatically triggered search-driven intelligent assistant that can:
- Answer almost any question with the latest, most accurate information
- Search for technical documentation and tutorials
- Troubleshoot common errors and issues
- Find configuration guides for software and tools
- Search for code examples of specific functionality
- Get recommended development best practices
- Stay updated on the latest developments in technology and industries

### 2. Webpage Summarization (kagi_summarize)

Quickly analyze and summarize webpage content:
- Extract main content from long articles
- Extract key information from webpages
- Get main points and conclusions from articles
- Save reading time
- Analyze technical documentation and open source projects
- Extract key findings from papers and research reports

### 3. Text Translation (kagi_translate)

High-quality text translation tool:
- Translate text from one language to another
- Maintain the original meaning and tone
- Suitable for various types of text, including technical documentation, literary works, etc.
- Support translation between multiple languages

## Intelligent Model Selection

The system uses Kagi's AI models, automatically selecting the most appropriate model based on the task type:

### Available Models
- **ki_quick**: Fast, direct answers (<5 seconds) - ideal for quick facts and general queries
- **ki_research**: Advanced deep research (>30 seconds) - best for complex analysis and detailed responses
- **ki_deep_research**: Experimental research engine - for specialized scientific research (higher cost)

### Conversation Model Selection
- **General Knowledge**: Quick model for everyday queries and factual information
- **Advanced Reasoning**: Research model for in-depth analysis and complex problem-solving
- **Balanced Performance**: Quick model for a good balance of speed and quality
- **Creative Content**: Research model for creative writing and diverse content generation
- **Technical Analysis**: Research model for precise technical understanding
- **Architecture Design**: Research model for system architecture analysis
- **Quick Response**: Quick model for fast, efficient responses
- **Code Generation**: Research model for robust code generation and debugging
- **Scientific Research**: Deep Research model for specialized domain exploration

### Summary Model Selection
- **Standard Summary**: Quick model for balanced and detailed content summaries
- **Comprehensive Analysis**: Research model for in-depth analysis and insights
- **Efficient Overview**: Quick model for concise overview of key points
- **Technical Breakdown**: Research model for detailed technical content analysis
- **Research Summary**: Deep Research model for academic or scientific content

### Translation Model Selection
- **Standard Translation**: Quick model for high-quality translation of general text
- **High Accuracy**: Research model for precise translation with nuanced understanding
- **Technical Translation**: Research model for accurate translation of professional content
- **Quick Translation**: Quick model for fast translation of simple content
- **Creative Translation**: Research model to preserve style and creative elements

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Kagi account and valid Cookie

### Installation Steps

1. Clone the repository or download the source code

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables
   Create a `.env` file in the project root directory and add your Kagi Cookie:
   ```
   KAGI_COOKIE=your_kagi_cookie_here
   ```
   
   How to get your Kagi Cookie:
   - Log in to the Kagi website (https://kagi.com)
   - Open browser developer tools (F12)
   - Go to the Network tab
   - Refresh the page
   - Find any request and look for the Cookie value in Headers
   - Copy the entire Cookie string

## Usage

### Starting the Service
```bash
python kagi.py
```

### Using Commands
- Regular questions will automatically use the `kagi_chat` tool
- Use the `/summarize [URL]` command to summarize webpage content
- Use the `/translate [text]` command to translate text

### Examples

1. Regular conversation (automatically uses kagi_chat):
   ```
   How to process JSON data in Python?
   ```

2. Webpage summarization:
   ```
   /summarize https://en.wikipedia.org/wiki/Artificial_intelligence
   ```

3. Text translation:
   ```
   /translate Python is a programming language that lets you work quickly and integrate systems more effectively. Chinese
   ```

## Advanced Features

### Caching Mechanism
The system implements a caching mechanism that can cache responses in non-session mode, improving response speed and reducing API calls.

### Session Management
The system automatically manages session context to maintain conversation coherence. You can start a new conversation by setting `new_conversation=True`.

### Custom Configuration
You can customize API configuration by modifying the `KagiConfig` class, such as timeout, user agent, etc.

## Technical Architecture

This project is built on the following technologies:
- **MCP (Model Control Protocol) v1.26.0**: For building and managing AI tools
- **FastMCP**: Fast implementation of MCP for creating AI services
- **Kagi API**: Provides high-quality AI responses and search capabilities
- **Requests**: For HTTP requests
- **HTML2Text**: For converting HTML to Markdown format
- **Python-dotenv**: For environment variable management
- **Pydantic v2**: For data validation and settings management

## Important Notes

- A valid Kagi Cookie is required to use the service
- Cookies have a limited validity period and need to be updated after expiration
- Please comply with Kagi's terms of use and limitations when using the API

## Contributions and Feedback

Contributions, issue reports, and feature requests are welcome. Please submit your feedback and contributions through GitHub Issues or Pull Requests.

## License

[MIT License](LICENSE)