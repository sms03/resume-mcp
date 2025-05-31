# Resume MCP Agent

An intelligent Model Context Protocol (MCP) server for AI-powered resume analysis and sorting. This system helps HR professionals and recruiters efficiently analyze resumes and match them with job descriptions using advanced NLP and machine learning techniques.

## Features

- **Resume Parsing**: Extract text from PDF and DOCX resume files
- **Job Description Matching**: Intelligent matching between resumes and job requirements
- **Skills Analysis**: Extract and analyze technical and soft skills
- **Experience Evaluation**: Assess work experience relevance and seniority
- **Education Matching**: Evaluate educational background against job requirements
- **Scoring System**: Comprehensive scoring algorithm for resume ranking
- **Web Interface**: Modern web UI for easy interaction
- **MCP Integration**: Full Model Context Protocol support for AI agents

## Technology Stack

- **Backend**: Python with FastAPI
- **MCP**: Model Context Protocol server implementation
- **AI/ML**: Google's ADK, spaCy, scikit-learn, transformers
- **Document Processing**: PyPDF2, python-docx
- **Web UI**: FastAPI with Jinja2 templates
- **Environment**: UV for dependency management and virtual environments

## Setup

### Prerequisites

- Python 3.9 or higher
- UV package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd resume-mcp
```

2. Create and activate virtual environment with UV:
```bash
uv venv
# On Windows
.venv\Scripts\activate
# On Unix/macOS
source .venv/bin/activate
```

3. Install dependencies:
```bash
uv pip install -e .
```

4. Download spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

5. Set up Google AI credentials (optional):
```bash
export GOOGLE_API_KEY="your-api-key"
```

## Usage

### Start the MCP Server

```bash
resume-mcp
```

### Web Interface

Navigate to `http://localhost:8000` to access the web interface.

### API Endpoints

- `POST /analyze/resume` - Analyze a single resume
- `POST /match/job` - Match resumes with job description
- `GET /resumes` - List all analyzed resumes
- `GET /jobs` - List all job descriptions

## Project Structure

```
resume-mcp/
├── src/
│   └── resume_mcp/
│       ├── __init__.py
│       ├── server.py              # MCP server implementation
│       ├── models/                # Data models
│       ├── analyzers/             # Resume and job analysis
│       ├── matching/              # Matching algorithms
│       ├── storage/               # Data storage
│       ├── web/                   # Web interface
│       └── utils/                 # Utility functions
├── templates/                     # HTML templates
├── static/                       # Static assets
├── tests/                        # Test suite
├── pyproject.toml                # Project configuration
└── README.md                     # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
