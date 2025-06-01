# Resume MCP Agent

A Model Context Protocol (MCP) server agent for analyzing resumes and sorting them according to job descriptions. This agent is compatible with the Claude desktop app and uses Google's ADK for AI capabilities.

## Features

- Resume parsing and analysis
- Matching resumes against job descriptions
- Ranking and sorting candidates
- Compatible with Claude desktop app

## Requirements

- Python 3.10+
- Google ADK
- UV package manager

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/resume-mcp.git
cd resume-mcp

# Create and activate a virtual environment
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
# source venv/bin/activate

# Install dependencies using UV
uv pip install -r requirements.txt
```

## Running the MCP Server

```bash
python src/main.py
```

## Usage with Claude Desktop App

This MCP server can be used as a plugin for the Claude desktop app. Configure the plugin in Claude by pointing to the local server address (default: `http://localhost:8080`).

## License

[MIT](LICENSE)
