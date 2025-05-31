"""
Resume Analysis Agent for Google Agent Development Kit (ADK)
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import json
from typing import Dict, Any, List
import os
import sys
from pathlib import Path
import asyncio

# Add the parent directory to the path so we can import our existing server
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.analyzer import ResumeAnalyzer
from src.config import Config
from src.models import JobRequirement, EducationLevel

# Initialize the analyzer components
config = Config()
analyzer = ResumeAnalyzer(config)

def analyze_resume(file_path: str) -> str:
    """
    Analyze a single resume file and provide comprehensive insights.
    
    Args:
        file_path: Path to the resume file to analyze
        
    Returns:
        Analysis results as a string
    """
    try:
        # Run the async method in a sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(analyzer.analyze_single_resume(file_path))
            
            # Format the result as a readable string
            response = {
                "candidate_name": result.resume.contact_info.name,
                "email": result.resume.contact_info.email,
                "phone": result.resume.contact_info.phone,
                "summary": result.resume.summary,
                "total_experience_years": result.resume.total_experience_years,
                "education_count": len(result.resume.education),
                "skills_count": len(result.resume.skills),
                "overall_score": result.score.overall_score,
                "experience_score": result.score.experience_score,
                "education_score": result.score.education_score,
                "skills_score": result.score.skills_score,
                "recommendation": result.score.recommendation,
                "processing_time_seconds": result.processing_time
            }
            
            return json.dumps(response, indent=2)
        finally:
            loop.close()
    except Exception as e:
        return f"Error analyzing resume: {str(e)}"

def batch_analyze_resumes(file_paths: List[str]) -> str:
    """
    Analyze multiple resume files in batch.
    
    Args:
        file_paths: List of paths to resume files to analyze
        
    Returns:
        Batch analysis results as a string
    """
    try:
        # Run the async method in a sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(analyzer.analyze_batch_resumes(file_paths))
            sorted_results = analyzer.sort_resumes_by_relevance(results)
            
            response = {
                "total_processed": len(results),
                "results": [
                    {
                        "rank": result.ranking,
                        "candidate_name": result.resume.contact_info.name,
                        "email": result.resume.contact_info.email,
                        "overall_score": result.score.overall_score,
                        "job_match_percentage": result.job_match_percentage,
                        "experience_years": result.resume.total_experience_years,
                        "skills_count": len(result.resume.skills),
                        "recommendation": result.score.recommendation[:100] + "..." if len(result.score.recommendation) > 100 else result.score.recommendation
                    }
                    for result in sorted_results
                ]
            }
            
            return json.dumps(response, indent=2)
        finally:
            loop.close()
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
        # Parse job requirements JSON
        job_req_dict = json.loads(job_requirements)
        
        # Create JobRequirement object
        education_level = EducationLevel.OTHER
        if "required_education" in job_req_dict:
            try:
                education_level = EducationLevel(job_req_dict["required_education"])
            except ValueError:
                pass
        
        job_req = JobRequirement(
            title=job_req_dict.get("title", ""),
            description=job_req_dict.get("description", ""),
            required_skills=job_req_dict.get("required_skills", []),
            preferred_skills=job_req_dict.get("preferred_skills", []),
            required_experience_years=job_req_dict.get("required_experience_years", 0),
            required_education=education_level,
            location=job_req_dict.get("location", ""),
            salary_range=job_req_dict.get("salary_range", "")
        )
        
        # Run the async method in a sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(analyzer.analyze_single_resume(file_path, job_req))
            
            response = {
                "candidate": result.resume.contact_info.name,
                "job_title": job_req.title,
                "overall_score": result.score.overall_score,
                "score_breakdown": {
                    "experience": result.score.experience_score,
                    "education": result.score.education_score,
                    "skills": result.score.skills_score,
                    "achievements": result.score.achievements_score
                },
                "job_match_percentage": result.job_match_percentage,
                "matching_skills": result.score.matching_skills,
                "missing_skills": result.score.missing_skills,
                "experience_gap_years": result.score.experience_gap,
                "recommendation": result.score.recommendation,
                "confidence": result.score.confidence
            }
            
            return json.dumps(response, indent=2)
        finally:
            loop.close()
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
    try:
        # Extract requirements from job description (simplified)
        # In practice, you'd use NLP for better extraction
        import re
        
        # Extract skills from job description
        common_skills = [
            "python", "java", "javascript", "react", "angular", "vue",
            "node.js", "express", "django", "flask", "sql", "aws", "docker"
        ]
        
        job_description_lower = job_description.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill in job_description_lower:
                found_skills.append(skill)
        
        # Extract experience requirements
        experience_years = 0
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*years?\s*(?:in|with)',
            r'minimum\s*(?:of\s*)?(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, job_description_lower)
            if match:
                experience_years = int(match.group(1))
                break
        
        # Create JobRequirement object
        job_req = JobRequirement(
            title="Extracted from description",
            description=job_description,
            required_skills=found_skills,
            required_experience_years=experience_years
        )
        
        # Run the async method in a sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(analyzer.analyze_batch_resumes(file_paths, job_req))
            sorted_results = analyzer.sort_resumes_by_relevance(results, job_req)
            
            # Return top 10 matches
            top_matches = sorted_results[:10]
            
            response = {
                "job_description_summary": job_description[:200] + "..." if len(job_description) > 200 else job_description,
                "extracted_requirements": {
                    "skills": job_req.required_skills,
                    "experience_years": job_req.required_experience_years
                },
                "total_candidates_analyzed": len(results),
                "top_matches": [
                    {
                        "rank": match.ranking,
                        "candidate_name": match.resume.contact_info.name,
                        "email": match.resume.contact_info.email,
                        "job_match_percentage": match.job_match_percentage,
                        "overall_score": match.score.overall_score,
                        "matching_skills": match.score.matching_skills,
                        "experience_years": match.resume.total_experience_years,
                        "recommendation": match.score.recommendation
                    }
                    for match in top_matches
                ]
            }
            
            return json.dumps(response, indent=2)
        finally:
            loop.close()
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
    try:
        # Run the async method in a sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(analyzer.analyze_batch_resumes(file_paths))
            
            # Extract and aggregate skills
            all_skills = {}
            skills_by_candidate = []
            
            for result in results:
                candidate_skills = []
                for skill in result.resume.skills:
                    skill_info = {
                        "name": skill.name,
                        "category": skill.category.value,
                        "proficiency_level": skill.proficiency_level,
                        "years_experience": skill.years_experience
                    }
                    candidate_skills.append(skill_info)
                    
                    # Aggregate for overall stats
                    if skill.name not in all_skills:
                        all_skills[skill.name] = {"count": 0, "category": skill.category.value}
                    all_skills[skill.name]["count"] += 1
                
                skills_by_candidate.append({
                    "candidate": result.resume.contact_info.name,
                    "file_path": result.resume.file_path,
                    "total_skills": len(candidate_skills),
                    "skills": candidate_skills
                })
            
            # Sort skills by frequency
            most_common_skills = sorted(all_skills.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
            
            response = {
                "skills_extraction": {
                    "total_candidates": len(results),
                    "total_unique_skills": len(all_skills),
                    "most_common_skills": [
                        {"skill": skill, "count": data["count"], "category": data["category"]}
                        for skill, data in most_common_skills
                    ],
                    "skills_by_candidate": skills_by_candidate
                }
            }
            
            return json.dumps(response, indent=2)
        finally:
            loop.close()
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
    name='resume_analysis_agent',
    description='A comprehensive resume analysis agent that can analyze, score, and match resumes to job requirements.',
    instruction='''You are a professional resume analysis expert. You can:

1. Analyze individual resumes for content, structure, and quality
2. Perform batch analysis of multiple resumes
3. Score resumes against specific job requirements
4. Match resumes to job descriptions and rank candidates
5. Extract skills from resumes

Always provide detailed, constructive feedback and actionable insights. When analyzing resumes, consider:
- Content quality and relevance
- Structure and formatting
- Skills alignment with requirements
- Experience depth and progression
- Overall presentation and professionalism

Use the available tools to perform these analyses based on user requests.''',
    tools=[
        analyze_resume_tool,
        batch_analyze_tool,
        score_resume_tool,
        match_job_tool,
        extract_skills_tool
    ]
)