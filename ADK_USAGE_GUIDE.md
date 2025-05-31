# ADK Web UI Usage Guide

## 🚀 Quick Start

### 1. Start the ADK Web Server
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start ADK-compatible web server
python adk_main.py
```

The server will start at: **http://localhost:3000**

### 2. Test the Server
```powershell
# Test server status
curl http://localhost:3000/

# Test health check
curl http://localhost:3000/health
```

## 📡 API Endpoints

### Basic Information
- **GET /** - Server information and status
- **GET /health** - Health check endpoint

### Resume Analysis
- **POST /analyze-resume** - Analyze a single resume
- **POST /batch-analyze** - Analyze multiple resumes
- **POST /upload-resume** - Upload and analyze resume file

### Scoring & Ranking
- **POST /score-resume** - Score resume against job requirements
- **POST /sort-resumes** - Sort and rank multiple resumes
- **POST /filter-resumes** - Filter resumes by criteria

### Job Matching
- **POST /match-job** - Find best matches for job description
- **POST /extract-skills** - Extract skills from resume
- **POST /generate-report** - Generate comprehensive analysis report

## 📋 Example API Calls

### Analyze Single Resume
```javascript
const response = await fetch('http://localhost:3000/analyze-resume', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_path: '/path/to/resume.pdf',
    job_requirements: {
      title: 'Software Engineer',
      required_skills: ['Python', 'JavaScript', 'React'],
      required_experience_years: 3
    }
  })
});
const result = await response.json();
```

### Batch Analysis
```javascript
const response = await fetch('http://localhost:3000/batch-analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_paths: [
      '/path/to/resume1.pdf',
      '/path/to/resume2.docx',
      '/path/to/resume3.txt'
    ],
    job_requirements: {
      title: 'Data Scientist',
      required_skills: ['Python', 'Machine Learning', 'SQL']
    }
  })
});
```

### Score Resume
```javascript
const response = await fetch('http://localhost:3000/score-resume', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_path: '/path/to/resume.pdf',
    job_requirements: {
      title: 'Senior Developer',
      required_skills: ['Python', 'Django', 'AWS'],
      required_experience_years: 5,
      required_education: 'bachelor'
    }
  })
});
```

### Job Matching
```javascript
const response = await fetch('http://localhost:3000/match-job', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_paths: ['/path/to/resume1.pdf', '/path/to/resume2.pdf'],
    job_description: `We are looking for a Python developer with 3+ years 
                     experience in web development, Django, and cloud platforms.`,
    max_results: 5
  })
});
```

### File Upload
```javascript
const formData = new FormData();
formData.append('file', resumeFile);

const response = await fetch('http://localhost:3000/upload-resume', {
  method: 'POST',
  body: formData
});
```

## 🔧 Configuration

### Environment Variables (.env)
```properties
# Web UI Settings
WEB_UI_ENABLED=true
MCP_TRANSPORT=http
SERVER_HOST=localhost
SERVER_PORT=3000

# CORS Settings
ENABLE_CORS=true
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# AI Configuration
AI_MODEL_NAME=gemini-2.0-flash
GOOGLE_API_KEY=your_api_key
GOOGLE_PROJECT_ID=your_project_id

# File Processing
MAX_FILE_SIZE_MB=10
SUPPORTED_FILE_TYPES=pdf,docx,txt
TEMP_DIR=./temp
```

## 📊 Response Format

All endpoints return JSON responses with this structure:

```json
{
  "resume_analysis": {
    "candidate_name": "John Doe",
    "email": "john@example.com",
    "overall_score": 0.85,
    "job_match_percentage": 78,
    "strengths": ["Strong Python skills", "Relevant experience"],
    "recommendation": "Excellent candidate for the position"
  }
}
```

## 🛠️ Error Handling

The API returns appropriate HTTP status codes:
- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: File not found
- **500**: Internal server error

Error responses include details:
```json
{
  "detail": "File not found: /path/to/resume.pdf"
}
```

## 🔗 Integration with ADK

1. Set your ADK web UI to connect to `http://localhost:3000`
2. Configure CORS origins to include your web UI domain
3. Use the HTTP endpoints instead of stdio transport
4. Handle file uploads through the `/upload-resume` endpoint

## 🎯 Next Steps

1. **Production Deployment**: Update CORS origins and add SSL
2. **Authentication**: Add API keys or OAuth for security
3. **Rate Limiting**: Implement rate limiting for production use
4. **Monitoring**: Add logging and metrics collection
5. **Scaling**: Consider load balancing for high volume

Your Resume MCP Server is now fully compatible with ADK Web UI! 🚀
