#!/usr/bin/env python3
"""
Resume MCP Server - A comprehensive resume analysis and job matching agent.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# MCP imports
try:
    from mcp.server import Server
    from mcp.types import Tool, Resource
    from mcp.server.stdio import stdio_server
except ImportError:
    print("MCP library not found. Please install with: pip install mcp")
    sys.exit(1)

# Local imports
from .analyzers.resume_analyzer import ResumeAnalyzer
from .analyzers.job_analyzer import JobAnalyzer
from .analyzers.resume_matcher import ResumeMatcher
from .storage.storage_manager import StorageManager
from .utils.file_processor import FileProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
resume_analyzer = ResumeAnalyzer()
job_analyzer = JobAnalyzer()
resume_matcher = ResumeMatcher()
storage_manager = StorageManager()
file_processor = FileProcessor()

# Create the MCP server
server = Server("resume-mcp")

# Initialize database
try:
    storage_manager.initialize_database()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="analyze_resume",
            description="Analyze a resume file and extract structured information",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_content": {
                        "type": "string",
                        "description": "Base64 encoded file content"
                    },
                    "filename": {
                        "type": "string", 
                        "description": "Name of the file"
                    }
                },
                "required": ["file_content", "filename"]
            }
        ),
        Tool(
            name="analyze_job_description",
            description="Analyze a job description and extract requirements",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_text": {
                        "type": "string",
                        "description": "Job description text"
                    },
                    "job_title": {
                        "type": "string",
                        "description": "Job title"
                    },
                    "company": {
                        "type": "string",
                        "description": "Company name (optional)"
                    }
                },
                "required": ["job_text", "job_title"]
            }
        ),
        Tool(
            name="match_resume_to_job",
            description="Match a specific resume to a job description",
            inputSchema={
                "type": "object",
                "properties": {
                    "resume_id": {
                        "type": "string",
                        "description": "Resume ID"
                    },
                    "job_id": {
                        "type": "string",
                        "description": "Job description ID"
                    }
                },
                "required": ["resume_id", "job_id"]
            }
        ),
        Tool(
            name="find_best_candidates",
            description="Find the best candidate resumes for a job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "Job description ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of candidates to return",
                        "default": 10
                    }
                },
                "required": ["job_id"]
            }
        ),
        Tool(
            name="search_resumes",
            description="Search resumes by criteria",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Required skills"
                    },
                    "experience_years": {
                        "type": "integer",
                        "description": "Minimum years of experience"
                    },
                    "education_level": {
                        "type": "string",
                        "description": "Minimum education level"
                    }
                }
            }
        ),
        Tool(
            name="get_resume_summary",
            description="Get a summary of a resume",
            inputSchema={
                "type": "object",
                "properties": {
                    "resume_id": {
                        "type": "string",
                        "description": "Resume ID"
                    }
                },
                "required": ["resume_id"]
            }
        )
    ]

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="resume://statistics",
            name="System Statistics",
            description="Overall system statistics and metrics"
        ),
        Resource(
            uri="resume://skills-database",
            name="Skills Database",
            description="Database of known skills and technologies"
        ),
        Resource(
            uri="resume://recent-activity",
            name="Recent Activity",
            description="Recent resume uploads and job postings"
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Handle tool calls."""
    try:
        if name == "analyze_resume":
            # Decode base64 content
            import base64
            file_content = base64.b64decode(arguments["file_content"])
            filename = arguments["filename"]
            
            # Extract text from file
            text = file_processor.extract_text(file_content, filename)
            if not text:
                return {"error": "Could not extract text from file"}
            
            # Analyze resume
            resume_data = resume_analyzer.analyze(text, filename)
            
            # Store in database
            resume_id = storage_manager.store_resume(resume_data)
            resume_data.id = resume_id
            
            return {
                "success": True,
                "resume_id": resume_id,
                "data": resume_data.model_dump(),
                "message": "Resume analyzed successfully"
            }
            
        elif name == "analyze_job_description":
            job_text = arguments["job_text"]
            job_title = arguments["job_title"]
            company = arguments.get("company", "")
            
            # Analyze job description
            job_data = job_analyzer.analyze(job_text, job_title, company)
            
            # Store in database
            job_id = storage_manager.store_job_description(job_data)
            job_data.id = job_id
            
            return {
                "success": True,
                "job_id": job_id,
                "data": job_data.model_dump(),
                "message": "Job description analyzed successfully"
            }
            
        elif name == "match_resume_to_job":
            resume_id = arguments["resume_id"]
            job_id = arguments["job_id"]
            
            # Get resume and job from database
            resume = storage_manager.get_resume(resume_id)
            job = storage_manager.get_job_description(job_id)
            
            if not resume or not job:
                return {"error": "Resume or job not found"}
            
            # Perform matching
            match_result = resume_matcher.match_resume_to_job(resume, job)
            
            return {
                "success": True,
                "match_result": match_result.model_dump(),
                "message": "Matching completed successfully"
            }
            
        elif name == "find_best_candidates":
            job_id = arguments["job_id"]
            limit = arguments.get("limit", 10)
            
            # Get job description
            job = storage_manager.get_job_description(job_id)
            if not job:
                return {"error": "Job not found"}
            
            # Get all resumes
            resumes = storage_manager.get_all_resumes()
            
            # Match each resume and sort by score
            matches = []
            for resume in resumes:
                try:
                    match_result = resume_matcher.match_resume_to_job(resume, job)
                    matches.append({
                        "resume_id": resume.id,
                        "resume_name": resume.contact_info.name or "Unknown",
                        "score": match_result.overall_match.score,
                        "match_details": match_result.model_dump()
                    })
                except Exception as e:
                    logger.warning(f"Error matching resume {resume.id}: {e}")
                    continue
            
            # Sort by score and return top candidates
            matches.sort(key=lambda x: x["score"], reverse=True)
            top_matches = matches[:limit]
            
            return {
                "success": True,
                "candidates": top_matches,
                "total_evaluated": len(matches),
                "message": f"Found {len(top_matches)} top candidates"
            }
            
        elif name == "search_resumes":
            query = arguments.get("query", "")
            skills = arguments.get("skills", [])
            experience_years = arguments.get("experience_years", 0)
            education_level = arguments.get("education_level", "")
            
            # Simple search implementation
            all_resumes = storage_manager.get_all_resumes()
            filtered_resumes = []
            
            for resume in all_resumes:
                # Check if resume matches criteria
                matches = True
                
                # Check skills
                if skills:
                    resume_skills = [skill.name.lower() for skill in resume.skills]
                    for required_skill in skills:
                        if required_skill.lower() not in resume_skills:
                            matches = False
                            break
                
                # Check experience
                if experience_years > 0:
                    if (resume.total_experience_years or 0) < experience_years:
                        matches = False
                
                # Check query in text
                if query:
                    if query.lower() not in resume.raw_text.lower():
                        matches = False
                
                if matches:
                    filtered_resumes.append({
                        "id": resume.id,
                        "name": resume.contact_info.name or "Unknown",
                        "experience_years": resume.total_experience_years,
                        "skills": [skill.name for skill in resume.skills[:10]],  # First 10 skills
                        "summary": resume.summary[:200] if resume.summary else ""
                    })
            
            return {
                "success": True,
                "results": filtered_resumes,
                "count": len(filtered_resumes),
                "message": f"Found {len(filtered_resumes)} matching resumes"
            }
            
        elif name == "get_resume_summary":
            resume_id = arguments["resume_id"]
            resume = storage_manager.get_resume(resume_id)
            
            if not resume:
                return {"error": "Resume not found"}
            
            return {
                "success": True,
                "summary": {
                    "id": resume.id,
                    "name": resume.contact_info.name or "Unknown",
                    "email": resume.contact_info.email,
                    "phone": resume.contact_info.phone,
                    "location": resume.contact_info.location,
                    "total_experience": resume.total_experience_years,
                    "skills_count": len(resume.skills),
                    "education_count": len(resume.education),
                    "work_experience_count": len(resume.work_experience),
                    "summary": resume.summary[:300] if resume.summary else ""
                },
                "message": "Resume summary retrieved successfully"
            }
        
        else:
            return {"error": f"Unknown tool: {name}"}
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return {"error": f"Tool execution failed: {str(e)}"}

@server.read_resource()
async def read_resource(uri: str) -> Any:
    """Handle resource requests."""
    try:
        if uri == "resume://statistics":
            stats = storage_manager.get_statistics()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(stats, indent=2)
                    }
                ]
            }
            
        elif uri == "resume://skills-database":
            # Get a sample of skills from the database
            skills_data = resume_analyzer._load_skills_database()
            sample_skills = dict(list(skills_data.items())[:50])  # First 50 skills
            
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": json.dumps(sample_skills, indent=2)
                    }
                ]
            }
            
        elif uri == "resume://recent-activity":
            # Get recent resumes and jobs
            recent_resumes = storage_manager.get_all_resumes(limit=10)
            recent_jobs = storage_manager.get_all_job_descriptions(limit=10)
            
            activity = {
                "recent_resumes": [
                    {
                        "id": r.id,
                        "filename": r.filename,
                        "name": r.contact_info.name or "Unknown",
                        "created_at": r.created_at.isoformat() if r.created_at else None
                    }
                    for r in recent_resumes
                ],
                "recent_jobs": [
                    {
                        "id": j.id,
                        "title": j.title,
                        "company": j.company,
                        "created_at": j.created_at.isoformat() if j.created_at else None
                    }
                    for j in recent_jobs
                ]
            }
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(activity, indent=2)
                    }
                ]
            }
        
        else:
            raise ValueError(f"Unknown resource: {uri}")
            
    except Exception as e:
        logger.error(f"Error getting resource {uri}: {str(e)}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }
            ]
        }

async def main():
    """Run the MCP server."""
    try:
        # Run the server
        async with stdio_server() as streams:
            await server.run(
                streams[0],  # read stream
                streams[1],  # write stream
                server.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
