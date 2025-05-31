#!/usr/bin/env python3
"""
Simple test for the Resume MCP matching functionality.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test imports
try:
    from resume_mcp.analyzers.resume_analyzer import ResumeAnalyzer
    from resume_mcp.analyzers.job_analyzer import JobAnalyzer
    from resume_mcp.analyzers.resume_matcher import ResumeMatcher
    from resume_mcp.models.schemas import ResumeData, JobPosting, MatchResult
    print("✓ All imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

async def test_complete_flow():
    """Test the complete resume analysis and matching flow."""
    print("\n🧪 Starting Simple Resume MCP Functionality Test...")
    
    # Initialize analyzers
    resume_analyzer = ResumeAnalyzer()
    job_analyzer = JobAnalyzer()
    matcher = ResumeMatcher()
    
    await resume_analyzer.initialize()
    await job_analyzer.initialize()
    
    # Sample resume text
    sample_resume = """
    John Smith
    Senior Software Engineer
    
    Contact:
    Email: john.smith@email.com
    Phone: (555) 123-4567
    Location: San Francisco, CA
    
    Experience:
    Senior Software Engineer at Google (2020-2023)
    - Developed microservices using Python and Go
    - Led a team of 5 engineers
    - Implemented CI/CD pipelines with Docker and Kubernetes
    
    Software Engineer at Facebook (2018-2020)
    - Built scalable web applications using React and Node.js
    - Optimized database queries reducing latency by 40%
    
    Education:
    Master of Science in Computer Science, Stanford University (2018)
    Bachelor of Science in Computer Science, UC Berkeley (2016)
    
    Skills:
    Programming: Python, Java, JavaScript, Go, C++
    Frameworks: React, Node.js, Django, Flask
    Cloud: AWS, GCP, Docker, Kubernetes
    Databases: PostgreSQL, MongoDB, Redis
    """
    
    # Sample job description
    sample_job = """
    Senior Python Developer
    
    Company: Tech Innovations Inc.
    Location: Remote
    Salary: $120,000 - $150,000
    
    Job Description:
    We are looking for a Senior Python Developer to join our dynamic team. 
    
    Requirements:
    - 5+ years of experience with Python development
    - Strong experience with Django and Flask frameworks
    - Knowledge of Docker and Kubernetes
    - Experience with AWS or GCP
    - Bachelor's degree in Computer Science or related field
    - Strong communication skills
    - Experience with agile methodologies
    
    Preferred Qualifications:
    - Master's degree in Computer Science
    - Experience with React and JavaScript
    - Knowledge of machine learning libraries
    - Previous leadership experience
    
    Responsibilities:
    - Design and implement scalable web applications
    - Collaborate with cross-functional teams
    - Mentor junior developers
    - Participate in code reviews and architecture discussions
    """
    
    try:
        # Test 1: Resume Analysis
        print("\n🔍 Testing Resume Analysis...")
        resume_data = await resume_analyzer.analyze(sample_resume, "john_smith.txt")
        
        # Add missing ID field
        resume_data.id = "test_resume_001"
        
        print(f"✓ Resume analysis successful")
        print(f"  - Name: {resume_data.contact_info.name if resume_data.contact_info else 'None'}")
        print(f"  - Skills found: {len(resume_data.skills)}")
        print(f"  - Experience entries: {len(resume_data.work_experience)}")
        print(f"  - Education entries: {len(resume_data.education)}")
        
        # Test 2: Job Analysis
        print("\n🔍 Testing Job Analysis...")
        job_data = await job_analyzer.analyze(
            sample_job,
            "Senior Python Developer",
            "Tech Innovations Inc."
        )
        
        # Add missing ID field
        job_data.id = "test_job_001"
        
        print(f"✓ Job analysis successful")
        print(f"  - Title: {job_data.title}")
        print(f"  - Company: {job_data.company}")
        print(f"  - Required skills: {len(job_data.required_skills)}")
        print(f"  - Preferred skills: {len(job_data.preferred_skills)}")
        
        # Test 3: Resume Matching
        print("\n🔍 Testing Resume Matching...")
        match_result = matcher.match_resume_to_job(resume_data, job_data)
        
        print(f"✓ Resume matching successful")
        print(f"  - Overall score: {match_result.overall_score:.2f}")
        print(f"  - Resume name: {match_result.resume_name}")
        print(f"  - Job title: {match_result.job_title}")
        print(f"  - Skill matches: {len(match_result.skill_matches)}")
        
        print("\n🎉 All tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

def main():
    """Main function to run all tests."""
    result = asyncio.run(test_complete_flow())
    if result:
        print("\n✅ Resume MCP functionality test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Resume MCP functionality test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
