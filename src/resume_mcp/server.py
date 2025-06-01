"""
MCP Server implementation for resume analysis
"""
import logging
import json
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from resume_mcp.mcp_types import (
    ModelContextMessage,
    ModelContextRequest,
    ModelContextResponse,
    Operation,
)
from resume_mcp.resume_analyzer import ResumeAnalyzer
from resume_mcp.utils import extract_text_from_resume

logger = logging.getLogger(__name__)

# Global resume analyzer instance
resume_analyzer = ResumeAnalyzer()

def setup_mcp_routes(app: FastAPI):
    """Set up the MCP routes for the FastAPI app"""
    
    @app.post("/mcp/")
    async def handle_mcp_request(request: ModelContextRequest) -> ModelContextResponse:
        """Handle MCP requests following the Model Context Protocol"""
        try:
            # Process the request based on the operation
            if request.operation == Operation.EXECUTE_FUNCTION:
                return await process_function_call(request)
            else:
                # Handle agent description or other operations
                return get_agent_description()
        except Exception as e:
            logger.error(f"Error processing MCP request: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/upload-resume/")
    async def upload_resume(file: UploadFile = File(...)):
        """Endpoint to upload a resume file"""
        try:
            # Extract text from resume
            content = await file.read()
            resume_text = extract_text_from_resume(content, file.filename)
            
            return {"filename": file.filename, "status": "success", "text_length": len(resume_text)}
        except Exception as e:
            logger.error(f"Error uploading resume: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/upload-job-description/")
    async def upload_job_description(
        job_title: str = Form(...),
        job_description: str = Form(...)
    ):
        """Endpoint to upload a job description"""
        try:
            return {
                "job_title": job_title,
                "status": "success",
                "description_length": len(job_description)
            }
        except Exception as e:
            logger.error(f"Error uploading job description: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

async def process_function_call(request: ModelContextRequest) -> ModelContextResponse:
    """Process a function execution request"""
    try:
        function_name = request.function_name
        params = request.parameters or {}
        
        # Dispatch to appropriate function handler
        if function_name == "analyze_resume":
            return await analyze_resume_handler(params, request.messages)
        elif function_name == "match_resume_to_job":
            return await match_resume_job_handler(params, request.messages)
        elif function_name == "rank_candidates":
            return await rank_candidates_handler(params, request.messages)
        else:
            raise ValueError(f"Unknown function: {function_name}")
            
    except Exception as e:
        logger.error(f"Error in function execution: {str(e)}")
        return ModelContextResponse(
            content=f"Error executing function: {str(e)}",
            function_response={"error": str(e)}
        )

async def analyze_resume_handler(params: Dict[str, Any], messages: List[ModelContextMessage]) -> ModelContextResponse:
    """Handle resume analysis requests"""
    resume_text = params.get("resume_text", "")
    if not resume_text:
        return ModelContextResponse(
            content="No resume text provided",
            function_response={"error": "Resume text is required"}
        )
    
    analysis = await resume_analyzer.analyze_resume(resume_text)
    
    return ModelContextResponse(
        content=f"Resume analyzed successfully. Found {len(analysis.get('skills', []))} skills.",
        function_response=analysis
    )

async def match_resume_job_handler(params: Dict[str, Any], messages: List[ModelContextMessage]) -> ModelContextResponse:
    """Handle resume-job matching requests"""
    resume_text = params.get("resume_text", "")
    job_description = params.get("job_description", "")
    
    if not resume_text or not job_description:
        return ModelContextResponse(
            content="Both resume text and job description are required",
            function_response={"error": "Missing required parameters"}
        )
    
    match_results = await resume_analyzer.match_resume_to_job(resume_text, job_description)
    
    return ModelContextResponse(
        content=f"Resume matched to job with score: {match_results.get('match_score', 0)}/100",
        function_response=match_results
    )

async def rank_candidates_handler(params: Dict[str, Any], messages: List[ModelContextMessage]) -> ModelContextResponse:
    """Handle candidate ranking requests"""
    resumes = params.get("resumes", [])
    job_description = params.get("job_description", "")
    
    if not resumes or not job_description:
        return ModelContextResponse(
            content="Both resumes and job description are required",
            function_response={"error": "Missing required parameters"}
        )
    
    rankings = await resume_analyzer.rank_candidates(resumes, job_description)
    
    return ModelContextResponse(
        content=f"Ranked {len(rankings)} candidates based on job fit",
        function_response={"rankings": rankings}
    )

def get_agent_description() -> ModelContextResponse:
    """Return the agent description for MCP discovery"""
    description = {
        "name": "Resume Analysis Agent",
        "description": "An MCP agent for analyzing resumes and matching them to job descriptions",
        "version": "0.1.0",
        "functions": [
            {
                "name": "analyze_resume",
                "description": "Analyze a resume to extract key information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resume_text": {
                            "type": "string",
                            "description": "The full text of the resume to analyze"
                        }
                    },
                    "required": ["resume_text"]
                }
            },
            {
                "name": "match_resume_to_job",
                "description": "Compare a resume against a job description to determine fit",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resume_text": {
                            "type": "string",
                            "description": "The full text of the resume"
                        },
                        "job_description": {
                            "type": "string",
                            "description": "The job description to match against"
                        }
                    },
                    "required": ["resume_text", "job_description"]
                }
            },
            {
                "name": "rank_candidates",
                "description": "Rank multiple resumes against a job description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resumes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "text": {"type": "string"}
                                }
                            },
                            "description": "Array of resume objects with id and text"
                        },
                        "job_description": {
                            "type": "string",
                            "description": "The job description to rank against"
                        }
                    },
                    "required": ["resumes", "job_description"]
                }
            }
        ]
    }
    
    return ModelContextResponse(
        content=json.dumps(description),
        function_response=description
    )
