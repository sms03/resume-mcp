"""Main MCP server implementation for resume analysis."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mcp import McpServer, Resource, Tool
from mcp.server.models import InitializeResult
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    GetResourceRequest,
    GetResourceResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
)

from .analyzers.resume_analyzer import ResumeAnalyzer
from .analyzers.job_analyzer import JobAnalyzer
from .matching.resume_matcher import ResumeMatcher
from .models.schemas import JobDescription, ResumeData, MatchResult
from .storage.storage_manager import StorageManager
from .utils.file_processor import FileProcessor
from .web.routes import create_web_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeMCPServer:
    """MCP server for resume analysis and matching."""
    
    def __init__(self):
        self.resume_analyzer = ResumeAnalyzer()
        self.job_analyzer = JobAnalyzer()
        self.resume_matcher = ResumeMatcher()
        self.storage_manager = StorageManager()
        self.file_processor = FileProcessor()
        
    async def initialize(self):
        """Initialize the server components."""
        await self.resume_analyzer.initialize()
        await self.job_analyzer.initialize()
        await self.storage_manager.initialize()
        logger.info("Resume MCP Server initialized successfully")
    
    async def analyze_resume(self, file_content: bytes, filename: str) -> ResumeData:
        """Analyze a resume file."""
        try:
            # Extract text from file
            text = await self.file_processor.extract_text(file_content, filename)
            
            # Analyze resume
            resume_data = await self.resume_analyzer.analyze(text, filename)
            
            # Store in database
            resume_id = await self.storage_manager.store_resume(resume_data)
            resume_data.id = resume_id
            
            return resume_data
        except Exception as e:
            logger.error(f"Error analyzing resume {filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")
    
    async def analyze_job_description(self, job_text: str, job_title: str) -> JobDescription:
        """Analyze a job description."""
        try:
            job_description = await self.job_analyzer.analyze(job_text, job_title)
            job_id = await self.storage_manager.store_job_description(job_description)
            job_description.id = job_id
            return job_description
        except Exception as e:
            logger.error(f"Error analyzing job description: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error analyzing job: {str(e)}")
    
    async def match_resumes_to_job(self, job_id: str, limit: int = 10) -> List[MatchResult]:
        """Match resumes to a job description."""
        try:
            job_description = await self.storage_manager.get_job_description(job_id)
            if not job_description:
                raise HTTPException(status_code=404, detail="Job description not found")
            
            resumes = await self.storage_manager.get_all_resumes()
            matches = []
            
            for resume in resumes:
                match_result = await self.resume_matcher.match(resume, job_description)
                matches.append(match_result)
            
            # Sort by score and return top matches
            matches.sort(key=lambda x: x.overall_score, reverse=True)
            return matches[:limit]
        except Exception as e:
            logger.error(f"Error matching resumes: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error matching resumes: {str(e)}")


# Create MCP server instance
resume_server = ResumeMCPServer()

# Define MCP tools
TOOLS = [
    Tool(
        name="analyze_resume",
        description="Analyze a resume file and extract relevant information",
        inputSchema={
            "type": "object",
            "properties": {
                "file_content": {"type": "string", "description": "Base64 encoded file content"},
                "filename": {"type": "string", "description": "Name of the resume file"},
            },
            "required": ["file_content", "filename"],
        },
    ),
    Tool(
        name="analyze_job_description",
        description="Analyze a job description and extract requirements",
        inputSchema={
            "type": "object",
            "properties": {
                "job_text": {"type": "string", "description": "Job description text"},
                "job_title": {"type": "string", "description": "Job title"},
            },
            "required": ["job_text", "job_title"],
        },
    ),
    Tool(
        name="match_resumes_to_job",
        description="Match resumes to a job description and return ranked results",
        inputSchema={
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "Job description ID"},
                "limit": {"type": "integer", "description": "Maximum number of matches to return", "default": 10},
            },
            "required": ["job_id"],
        },
    ),
    Tool(
        name="get_resume_by_id",
        description="Get a specific resume by ID",
        inputSchema={
            "type": "object",
            "properties": {
                "resume_id": {"type": "string", "description": "Resume ID"},
            },
            "required": ["resume_id"],
        },
    ),
    Tool(
        name="list_resumes",
        description="List all analyzed resumes",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Maximum number of resumes to return", "default": 50},
            },
        },
    ),
    Tool(
        name="list_jobs",
        description="List all job descriptions",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Maximum number of jobs to return", "default": 50},
            },
        },
    ),
]

# Define MCP resources
RESOURCES = [
    Resource(
        uri="resume://statistics",
        name="Resume Statistics",
        description="Get statistics about analyzed resumes",
        mimeType="application/json",
    ),
    Resource(
        uri="resume://skills",
        name="Skills Database",
        description="Get comprehensive skills database",
        mimeType="application/json",
    ),
]


# MCP Server Implementation
mcp_server = McpServer("resume-analyzer")


@mcp_server.list_resources()
async def handle_list_resources() -> ListResourcesResult:
    """List available resources."""
    return ListResourcesResult(resources=RESOURCES)


@mcp_server.get_resource()
async def handle_get_resource(request: GetResourceRequest) -> GetResourceResult:
    """Get a specific resource."""
    if request.uri == "resume://statistics":
        stats = await resume_server.storage_manager.get_statistics()
        return GetResourceResult(
            contents=[
                {
                    "uri": request.uri,
                    "mimeType": "application/json",
                    "text": json.dumps(stats, indent=2),
                }
            ]
        )
    elif request.uri == "resume://skills":
        skills = await resume_server.storage_manager.get_skills_database()
        return GetResourceResult(
            contents=[
                {
                    "uri": request.uri,
                    "mimeType": "application/json",
                    "text": json.dumps(skills, indent=2),
                }
            ]
        )
    else:
        raise ValueError(f"Unknown resource: {request.uri}")


@mcp_server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(tools=TOOLS)


@mcp_server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls."""
    try:
        if request.name == "analyze_resume":
            import base64
            file_content = base64.b64decode(request.arguments["file_content"])
            filename = request.arguments["filename"]
            result = await resume_server.analyze_resume(file_content, filename)
            return CallToolResult(content=[{"type": "text", "text": json.dumps(result.dict(), indent=2)}])
        
        elif request.name == "analyze_job_description":
            job_text = request.arguments["job_text"]
            job_title = request.arguments["job_title"]
            result = await resume_server.analyze_job_description(job_text, job_title)
            return CallToolResult(content=[{"type": "text", "text": json.dumps(result.dict(), indent=2)}])
        
        elif request.name == "match_resumes_to_job":
            job_id = request.arguments["job_id"]
            limit = request.arguments.get("limit", 10)
            results = await resume_server.match_resumes_to_job(job_id, limit)
            return CallToolResult(content=[{"type": "text", "text": json.dumps([r.dict() for r in results], indent=2)}])
        
        elif request.name == "get_resume_by_id":
            resume_id = request.arguments["resume_id"]
            result = await resume_server.storage_manager.get_resume(resume_id)
            if result:
                return CallToolResult(content=[{"type": "text", "text": json.dumps(result.dict(), indent=2)}])
            else:
                return CallToolResult(content=[{"type": "text", "text": "Resume not found"}])
        
        elif request.name == "list_resumes":
            limit = request.arguments.get("limit", 50)
            results = await resume_server.storage_manager.get_all_resumes(limit=limit)
            return CallToolResult(content=[{"type": "text", "text": json.dumps([r.dict() for r in results], indent=2)}])
        
        elif request.name == "list_jobs":
            limit = request.arguments.get("limit", 50)
            results = await resume_server.storage_manager.get_all_job_descriptions(limit=limit)
            return CallToolResult(content=[{"type": "text", "text": json.dumps([j.dict() for j in results], indent=2)}])
        
        else:
            raise ValueError(f"Unknown tool: {request.name}")
    
    except Exception as e:
        logger.error(f"Error in tool call {request.name}: {str(e)}")
        return CallToolResult(
            content=[{"type": "text", "text": f"Error: {str(e)}"}],
            isError=True
        )


# FastAPI Web Application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    await resume_server.initialize()
    yield


app = FastAPI(
    title="Resume MCP Agent",
    description="AI-powered resume analysis and sorting system",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Add web routes
create_web_routes(app, resume_server, templates)


# API Routes
@app.post("/api/analyze/resume")
async def api_analyze_resume(
    file: UploadFile = File(...),
) -> JSONResponse:
    """API endpoint to analyze a resume."""
    try:
        content = await file.read()
        result = await resume_server.analyze_resume(content, file.filename)
        return JSONResponse(content=result.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/job")
async def api_analyze_job(
    job_text: str = Form(...),
    job_title: str = Form(...),
) -> JSONResponse:
    """API endpoint to analyze a job description."""
    try:
        result = await resume_server.analyze_job_description(job_text, job_title)
        return JSONResponse(content=result.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/match/{job_id}")
async def api_match_resumes(job_id: str, limit: int = 10) -> JSONResponse:
    """API endpoint to match resumes to a job."""
    try:
        results = await resume_server.match_resumes_to_job(job_id, limit)
        return JSONResponse(content=[r.dict() for r in results])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/resumes")
async def api_list_resumes(limit: int = 50) -> JSONResponse:
    """API endpoint to list resumes."""
    try:
        results = await resume_server.storage_manager.get_all_resumes(limit=limit)
        return JSONResponse(content=[r.dict() for r in results])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs")
async def api_list_jobs(limit: int = 50) -> JSONResponse:
    """API endpoint to list jobs."""
    try:
        results = await resume_server.storage_manager.get_all_job_descriptions(limit=limit)
        return JSONResponse(content=[j.dict() for j in results])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def main():
    """Main entry point for the MCP server."""
    # Initialize the server
    await resume_server.initialize()
    
    # Run the MCP server via stdio
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializeResult(
                protocolVersion="2024-11-05",
                capabilities=mcp_server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
                serverInfo={"name": "resume-analyzer", "version": "0.1.0"},
            ),
        )


def run_web_server():
    """Run the web server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # Run both MCP server and web server
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        run_web_server()
    else:
        asyncio.run(main())
