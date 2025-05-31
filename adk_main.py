"""
ADK Web UI Compatible Entry Point for Resume Analysis MCP Server
This version provides web UI compatibility for the Agent Development Kit
"""

import asyncio
import logging
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server

# For web UI compatibility
try:
    from fastapi import FastAPI, HTTPException, UploadFile, File
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
    FastAPI = FastAPI
    HTTPException = HTTPException
    UploadFile = UploadFile
    File = File
    CORSMiddleware = CORSMiddleware
    JSONResponse = JSONResponse
    uvicorn = uvicorn
    HAS_FASTAPI = True
except ImportError:
    FastAPI = None
    HTTPException = None
    UploadFile = None
    File = None
    CORSMiddleware = None
    JSONResponse = None
    uvicorn = None
    HAS_FASTAPI = False
    logging.warning("FastAPI not available. Web UI features will be limited.")

from src.server import ResumeAnalysisServer
from src.config import Config

# Load environment variables
load_dotenv()

def setup_logging():
    """Setup logging configuration"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('resume_mcp_adk.log')
        ]
    )

def create_web_app() -> Optional[FastAPI]:
    """Create FastAPI web application for ADK integration"""
    if not HAS_FASTAPI:
        return None
    
    app = FastAPI(
        title="Resume Analysis MCP Server",
        description="ADK-compatible resume analysis and candidate selection",
        version="1.0.0"
    )
    
    # Configure CORS for ADK web UI
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize resume server
    config = Config()
    resume_server = ResumeAnalysisServer(config)
    
    @app.get("/")
    async def root() -> Dict[str, Any]:
        """Root endpoint"""
        return {
            "name": "Resume Analysis MCP Server",
            "version": "1.0.0",
            "status": "running",
            "adk_compatible": True,
            "transport": "http+stdio"
        }
    
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "config_valid": True
        }
    
    @app.post("/analyze-resume")
    async def analyze_resume_endpoint(
        file_path: str,
        job_requirements: Optional[Dict[str, Any]] = None
    ):
        """Analyze a single resume"""
        try:
            args = {"file_path": file_path}
            if job_requirements:
                args["job_requirements"] = job_requirements
            
            result = await resume_server._handle_analyze_resume(args)
            return JSONResponse(content=json.loads(result[0].text))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/batch-analyze")
    async def batch_analyze_endpoint(
        file_paths: List[str],
        job_requirements: Optional[Dict[str, Any]] = None
    ):
        """Analyze multiple resumes"""
        try:
            args = {"file_paths": file_paths}
            if job_requirements:
                args["job_requirements"] = job_requirements
            
            result = await resume_server._handle_batch_analyze_resumes(args)
            return JSONResponse(content=json.loads(result[0].text))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/score-resume")
    async def score_resume_endpoint(
        file_path: str,
        job_requirements: Dict[str, Any]
    ):
        """Score a resume against job requirements"""
        try:
            args = {
                "file_path": file_path,
                "job_requirements": job_requirements
            }
            
            result = await resume_server._handle_score_resume(args)
            return JSONResponse(content=json.loads(result[0].text))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/sort-resumes")
    async def sort_resumes_endpoint(
        file_paths: List[str],
        job_requirements: Optional[Dict[str, Any]] = None,
        sort_criteria: str = "overall_score"
    ):
        """Sort and rank resumes"""
        try:
            args = {
                "file_paths": file_paths,
                "sort_criteria": sort_criteria
            }
            if job_requirements:
                args["job_requirements"] = job_requirements
            
            result = await resume_server._handle_sort_resumes(args)
            return JSONResponse(content=json.loads(result[0].text))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/filter-resumes")
    async def filter_resumes_endpoint(
        file_paths: List[str],
        filters: Dict[str, Any]
    ):
        """Filter resumes by criteria"""
        try:
            args = {
                "file_paths": file_paths,
                "filters": filters
            }
            
            result = await resume_server._handle_filter_resumes(args)
            return JSONResponse(content=json.loads(result[0].text))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/match-job")
    async def match_job_endpoint(
        file_paths: List[str],
        job_description: str,
        max_results: int = 10
    ):
        """Match resumes to job description"""
        try:
            args = {
                "file_paths": file_paths,
                "job_description": job_description,
                "max_results": max_results
            }
            
            result = await resume_server._handle_match_job(args)
            return JSONResponse(content=json.loads(result[0].text))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/extract-skills")
    async def extract_skills_endpoint(
        file_path: str,
        skill_categories: List[str] = ["technical", "soft"]
    ):
        """Extract skills from resume"""
        try:
            args = {
                "file_path": file_path,
                "skill_categories": skill_categories
            }
            
            result = await resume_server._handle_extract_skills(args)
            return JSONResponse(content=json.loads(result[0].text))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/generate-report")
    async def generate_report_endpoint(
        file_paths: List[str],
        job_requirements: Optional[Dict[str, Any]] = None,
        report_format: str = "detailed"
    ):
        """Generate analysis report"""
        try:
            args = {
                "file_paths": file_paths,
                "report_format": report_format
            }
            if job_requirements:
                args["job_requirements"] = job_requirements
            
            result = await resume_server._handle_generate_report(args)
            return JSONResponse(content=json.loads(result[0].text))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/upload-resume")
    async def upload_resume_endpoint(file: UploadFile = File(...)):
        """Upload and analyze resume file"""
        try:
            # Save uploaded file temporarily
            temp_dir = Path(os.getenv('TEMP_DIR', './temp'))
            temp_dir.mkdir(exist_ok=True)
            
            file_path = temp_dir / file.filename
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Analyze the uploaded file
            args = {"file_path": str(file_path)}
            result = await resume_server._handle_analyze_resume(args)
            
            # Cleanup temp file
            file_path.unlink(missing_ok=True)
            
            return JSONResponse(content=json.loads(result[0].text))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

async def run_mcp_server():
    """Run the standard MCP server (stdio transport)"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize configuration
        config = Config()
        
        # Create the resume analysis server
        resume_server = ResumeAnalysisServer(config)
        
        # Initialize the MCP server
        server = Server("resume-analysis-server")
        
        # Register tools with the server
        await resume_server.register_tools(server)
        
        logger.info("Starting Resume Analysis MCP Server (stdio)...")
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
            
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        raise

async def run_web_server():
    """Run the web server for ADK integration"""
    if not HAS_FASTAPI:
        raise RuntimeError("FastAPI is required for web server mode")
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        app = create_web_app()
        if not app:
            raise RuntimeError("Failed to create web application")
        
        host = os.getenv('SERVER_HOST', 'localhost')
        port = int(os.getenv('SERVER_PORT', '3000'))
        
        logger.info(f"Starting Resume Analysis Web Server on {host}:{port}...")
        
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level=os.getenv('LOG_LEVEL', 'info').lower(),
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")
        raise

async def main():
    """Main entry point - choose transport mode based on configuration"""
    transport_mode = os.getenv('MCP_TRANSPORT', 'stdio').lower()
    web_ui_enabled = os.getenv('WEB_UI_ENABLED', 'false').lower() == 'true'
    
    if web_ui_enabled and transport_mode == 'http':
        # Run web server for ADK integration
        await run_web_server()
    elif transport_mode == 'stdio':
        # Run standard MCP server
        await run_mcp_server()
    else:
        # Run both concurrently
        await asyncio.gather(
            run_mcp_server(),
            run_web_server() if HAS_FASTAPI else asyncio.sleep(0)
        )

if __name__ == "__main__":
    asyncio.run(main())
