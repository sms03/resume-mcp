"""
Simple Mock Resume Analysis Agent for ADK Testing
This version works without Google AI APIs for testing purposes
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import json
from typing import List, Dict, Any
import os
from pathlib import Path

def analyze_resume(file_path: str) -> str:
    """
    Analyze a single resume file and provide comprehensive insights.
    
    Args:
        file_path: Path to the resume file to analyze
        
    Returns:
        Analysis results as a string
    """
    try:
        # Mock analysis - in a real implementation this would parse the file
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"
        
        # Get file info
        file_size = os.path.getsize(file_path)
        file_ext = Path(file_path).suffix.lower()
        
        # Generate mock analysis
        response = {
            "resume_analysis": {
                "file_path": file_path,
                "file_size_bytes": file_size,
                "file_format": file_ext,
                "candidate_name": "John Doe (Mock)",
                "email": "john.doe@example.com",
                "phone": "+1-555-0123",
                "summary": "Experienced software developer with 5 years in web development",
                "total_experience_years": 5,
                "education_count": 2,
                "skills_count": 15,
                "parsing_confidence": 0.85
            },
            "scoring": {
                "overall_score": 0.78,
                "experience_score": 0.80,
                "education_score": 0.75,
                "skills_score": 0.82,
                "achievements_score": 0.70,
                "matching_skills": ["Python", "JavaScript", "React", "SQL"],
                "missing_skills": ["Docker", "Kubernetes"],
                "recommendation": "Strong candidate with good technical skills. Consider for technical interview.",
                "confidence": 0.85
            },
            "processing_time_seconds": 0.5,
            "note": "This is a mock analysis for ADK testing purposes"
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return f"Error analyzing resume: {str(e)}"

def batch_analyze_resumes(file_paths: List[str]) -> str:
    """
    Analyze multiple resume files in batch.
    
    Args:
        file_paths: List of paths to resume files to analyze
        
    Returns:
        Batch analysis results as a string
    """    try:
        results: List[Dict[str, Any]] = []
        for i, file_path in enumerate(file_paths):
            if os.path.exists(file_path):
                results.append({
                    "rank": i + 1,
                    "file_path": file_path,
                    "candidate_name": f"Candidate {i + 1} (Mock)",
                    "email": f"candidate{i + 1}@example.com",
                    "overall_score": 0.75 + (i * 0.05),  # Varying scores
                    "job_match_percentage": 70 + (i * 5),
                    "experience_years": 3 + i,
                    "skills_count": 10 + (i * 2),
                    "recommendation": f"Good candidate #{i + 1} for consideration"                })
        
        response: Dict[str, Any] = {
            "batch_analysis": {
                "total_processed": len(results),
                "total_requested": len(file_paths),
                "average_score": sum(r["overall_score"] for r in results) / len(results) if results else 0,
                "processing_completed": True,
                "note": "This is a mock analysis for ADK testing purposes"
            },
            "results": results
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return f"Error in batch analysis: {str(e)}"

def score_resume(file_path: str, job_requirements: str) -> str:
    """
    Score a resume against specific job requirements.
    
    Args:
        file_path: Path to the resume file
        job_requirements: Job requirements to score against (JSON string)
        
    Returns:
        Resume score and analysis as a string
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"
        
        # Parse job requirements if provided
        try:
            job_req = json.loads(job_requirements) if job_requirements else {}
        except:
            job_req = {"title": "General Position"}
        
        response = {
            "scoring_analysis": {
                "candidate": "John Doe (Mock)",
                "job_title": job_req.get("title", "General Position"),
                "overall_score": 0.82,
                "score_breakdown": {
                    "experience": 0.85,
                    "education": 0.78,
                    "skills": 0.88,
                    "achievements": 0.75
                },
                "job_match_percentage": 84,
                "matching_skills": job_req.get("required_skills", ["Python", "JavaScript"])[:4],
                "missing_skills": ["Docker", "AWS"],
                "experience_gap_years": 0,
                "recommendation": "Excellent match for the position. Recommend for interview.",
                "confidence": 0.88,
                "note": "This is a mock analysis for ADK testing purposes"
            }
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return f"Error scoring resume: {str(e)}"

def match_job(file_paths: List[str], job_description: str) -> str:
    """
    Match resumes to a job description and rank them.
    
    Args:
        file_paths: List of paths to resume files
        job_description: Job description to match against
        
    Returns:
        Job matching results as a string
    """
    try:        # Extract basic info from job description
        keywords: List[str] = ["python", "javascript", "react", "sql", "aws"]
        found_skills: List[str] = [skill for skill in keywords if skill.lower() in job_description.lower()]
        
        top_matches: List[Dict[str, Any]] = []
        for i, file_path in enumerate(file_paths[:5]):  # Top 5 matches
            if os.path.exists(file_path):
                top_matches.append({
                    "rank": i + 1,
                    "candidate_name": f"Candidate {i + 1} (Mock)",
                    "email": f"candidate{i + 1}@example.com",
                    "job_match_percentage": 90 - (i * 5),
                    "overall_score": 0.85 - (i * 0.05),
                    "matching_skills": found_skills[:3 + i],
                    "experience_years": 5 + i,
                    "recommendation": f"Top {i + 1} candidate - excellent fit"
                })
        
        response = {
            "job_matching": {
                "job_description_summary": job_description[:200] + "..." if len(job_description) > 200 else job_description,
                "extracted_requirements": {
                    "skills": found_skills,
                    "experience_years": 3
                },
                "total_candidates_analyzed": len(file_paths),
                "top_matches": top_matches,
                "note": "This is a mock analysis for ADK testing purposes"
            }
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return f"Error matching job: {str(e)}"

def extract_skills(file_paths: List[str]) -> str:
    """
    Extract skills from resume files.
    
    Args:
        file_paths: List of paths to resume files
        
    Returns:
        Extracted skills as a string
    """
    try:        # Mock skills data
        mock_skills: List[Dict[str, Any]] = [
            {"name": "Python", "category": "technical", "count": 8},
            {"name": "JavaScript", "category": "technical", "count": 6},
            {"name": "React", "category": "technical", "count": 5},
            {"name": "SQL", "category": "technical", "count": 7},
            {"name": "Leadership", "category": "soft", "count": 4},
            {"name": "Communication", "category": "soft", "count": 9},
        ]
        
        skills_by_candidate: List[Dict[str, Any]] = []
        for i, file_path in enumerate(file_paths):
            if os.path.exists(file_path):
                candidate_skills = mock_skills[:4 + i % 3]  # Varying skills per candidate
                skills_by_candidate.append({
                    "candidate": f"Candidate {i + 1} (Mock)",
                    "file_path": file_path,
                    "total_skills": len(candidate_skills),
                    "skills": candidate_skills                })
        
        response: Dict[str, Any] = {
            "skills_extraction": {
                "total_candidates": len(file_paths),
                "total_unique_skills": len(mock_skills),
                "most_common_skills": mock_skills,
                "skills_by_candidate": skills_by_candidate,
                "note": "This is a mock analysis for ADK testing purposes"
            }
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return f"Error extracting skills: {str(e)}"

# Create function tools
analyze_resume_tool = FunctionTool(analyze_resume)
batch_analyze_tool = FunctionTool(batch_analyze_resumes)
score_resume_tool = FunctionTool(score_resume)
match_job_tool = FunctionTool(match_job)
extract_skills_tool = FunctionTool(extract_skills)

# Create the agent with tools
root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='resume_analysis_agent_mock',
    description='A mock resume analysis agent for testing ADK integration without requiring Google AI APIs.',
    instruction='''You are a mock resume analysis expert for testing purposes. You can:

1. Analyze individual resumes for content, structure, and quality (mock data)
2. Perform batch analysis of multiple resumes (mock data)
3. Score resumes against specific job requirements (mock data)
4. Match resumes to job descriptions and rank candidates (mock data)
5. Extract skills from resumes (mock data)

NOTE: This is a testing version that returns mock data to demonstrate the ADK integration. 
All analysis results are simulated for demonstration purposes.

When users ask for resume analysis, explain that this is a mock version and show them the available tools and mock results.''',
    tools=[
        analyze_resume_tool,
        batch_analyze_tool,
        score_resume_tool,
        match_job_tool,
        extract_skills_tool
    ]
)
