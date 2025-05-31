# Resume Analysis MCP Server

An intelligent MCP server for resume analysis, sorting, and selection using Python and Google Agent Development Kit.

## Features

- **Resume Parsing**: Extract structured data from PDF, DOCX, and TXT resume files
- **Skills Analysis**: Identify and categorize technical and soft skills
- **Experience Evaluation**: Analyze work experience, education, and career progression
- **Resume Scoring**: Score resumes based on job requirements and criteria
- **Batch Processing**: Analyze multiple resumes simultaneously
- **Intelligent Sorting**: Rank candidates based on relevance and qualifications
- **Job Matching**: Match resumes to specific job descriptions
- **Report Generation**: Generate detailed analysis reports

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd resume-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Google Cloud credentials
```

4. Download required NLP models:
```bash
python -c "import spacy; spacy.cli.download('en_core_web_sm')"
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Usage

1. Start the MCP server:
```bash
python main.py
```

2. The server will be available for MCP connections on the configured port.

## Configuration

Configure the server through environment variables in `.env`:

- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your service account key
- `MCP_SERVER_PORT`: Port for MCP server (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)

## API Endpoints

The MCP server provides the following tools:

- `analyze_resume`: Analyze a single resume file
- `batch_analyze_resumes`: Analyze multiple resumes
- `score_resume`: Score a resume against job criteria
- `sort_resumes`: Sort resumes by relevance
- `match_job`: Match resumes to job descriptions
- `extract_skills`: Extract skills from resume text
- `generate_report`: Generate analysis report

## License

MIT License
