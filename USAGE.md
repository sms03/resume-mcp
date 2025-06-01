# Resume MCP Agent Usage Guide

This guide explains how to use the Resume MCP Agent, especially with the Claude desktop app.

## Setup and Installation

### Prerequisites

1. Python 3.10 or higher
2. UV package manager
3. Google API key for ADK

### Installation Steps

1. Clone the repository
   ```powershell
   git clone https://github.com/yourusername/resume-mcp.git
   cd resume-mcp
   ```

2. Run the setup script
   ```powershell
   python setup.py
   ```

3. Activate the virtual environment
   ```powershell
   # On Windows
   .\venv\Scripts\Activate
   
   # On Unix/MacOS
   # source venv/bin/activate
   ```

4. Configure your API keys
   - Copy `.env.example` to `.env`
   - Edit `.env` and add your Google API key

5. Run the server
   ```powershell
   python run.py
   ```

## Integration with Claude Desktop App

The Claude desktop app supports MCP (Model Context Protocol) agents as plugins. To integrate this resume analysis agent:

1. Make sure the MCP server is running on your local machine (default: `http://localhost:8080`)

2. In the Claude desktop app:
   - Go to Settings
   - Select "Plugins"
   - Click "Add Plugin"
   - Enter the URL of your MCP server (`http://localhost:8080/mcp/`)
   - Approve the plugin permissions

3. You can now use the Resume Analysis capabilities directly from within Claude

## Using the Resume Analysis Features

### Analyzing Resumes

To analyze a resume, you can use one of these approaches:

1. **Through the Claude Desktop App:**
   - Upload a resume via the Claude interface
   - Ask Claude to analyze the resume using the Resume MCP Agent
   - Example: "Analyze this resume and extract key information"

2. **Direct API Usage:**
   - Send a POST request to `/mcp/` with the resume text
   - Example:
     ```json
     {
       "operation": "EXECUTE_FUNCTION",
       "function_name": "analyze_resume",
       "parameters": {
         "resume_text": "...resume content here..."
       }
     }
     ```

### Matching Resumes to Job Descriptions

To compare a resume against a job description:

1. **Through Claude Desktop App:**
   - Upload a resume and provide a job description
   - Ask Claude to match the resume to the job
   - Example: "How well does this resume match this job description?"

2. **Direct API Usage:**
   - Send a POST request to `/mcp/`
   - Example:
     ```json
     {
       "operation": "EXECUTE_FUNCTION",
       "function_name": "match_resume_to_job",
       "parameters": {
         "resume_text": "...resume content here...",
         "job_description": "...job description here..."
       }
     }
     ```

### Ranking Multiple Candidates

To rank multiple candidates based on their resumes:

1. **Through Claude Desktop App:**
   - Upload multiple resumes and provide a job description
   - Ask Claude to rank the candidates
   - Example: "Rank these candidates for this position"

2. **Direct API Usage:**
   - Send a POST request to `/mcp/`
   - Example:
     ```json
     {
       "operation": "EXECUTE_FUNCTION",
       "function_name": "rank_candidates",
       "parameters": {
         "resumes": [
           {"id": "candidate1", "text": "...resume content..."},
           {"id": "candidate2", "text": "...resume content..."}
         ],
         "job_description": "...job description here..."
       }
     }
     ```

## Best Practices

1. **Resume Formats:**
   - PDF files work best
   - Word documents may require additional dependencies
   - Plain text files are supported but may lose formatting

2. **Job Descriptions:**
   - Include detailed requirements and qualifications
   - List both required and preferred skills
   - Specify experience level expectations

3. **Candidate Ranking:**
   - For best results, limit batches to 10 resumes at a time
   - Provide detailed job descriptions for more accurate matching

## Troubleshooting

1. **API Key Issues:**
   - Ensure your Google API key is correctly set in the `.env` file
   - Verify that your API key has access to the Gemini models

2. **Connection Problems:**
   - Check that the server is running (`python run.py`)
   - Verify the server address in Claude desktop app settings

3. **Parse Errors:**
   - Some PDFs may not extract text correctly
   - Try converting problematic files to plain text

4. **Memory Issues:**
   - Processing many resumes simultaneously may require more memory
   - Use the batch processing feature for large jobs
