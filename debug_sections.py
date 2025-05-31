#!/usr/bin/env python3
"""Debug script for section extraction."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from resume_mcp.analyzers.resume_analyzer import ResumeAnalyzer

async def debug_sections():
    """Debug what sections are found in the resume."""
    
    analyzer = ResumeAnalyzer()
    await analyzer.initialize()
    
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
      # Extract sections using internal method
    cleaned_text = analyzer._clean_text(sample_resume)
    print("=== CLEANED TEXT ===")
    print(repr(cleaned_text))
    print("\n=== LINES BEING PROCESSED ===")
    lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
    for i, line in enumerate(lines[:15]):  # Show first 15 lines
        print(f"{i+1:2d}: {line}")
    
    sections = analyzer._extract_sections(cleaned_text)
    
    print("=== DETECTED SECTIONS ===")
    for section_name, section_content in sections.items():
        print(f"\n📁 Section: {section_name}")
        print(f"Content (first 200 chars): {section_content[:200]}...")
    
    print("\n=== EXPERIENCE SECTION DETAIL ===")
    experience_text = sections.get("experience", "")
    if experience_text:
        print(f"Experience content: {experience_text}")
        experiences = analyzer._extract_work_experience(experience_text)
        print(f"Extracted {len(experiences)} work experiences")
        for i, exp in enumerate(experiences):
            print(f"  {i+1}. {exp.title} at {exp.company}")
    else:
        print("No experience section found!")
        
    print("\n=== EDUCATION SECTION DETAIL ===")
    education_text = sections.get("education", "")
    if education_text:
        print(f"Education content: {education_text}")
        education = analyzer._extract_education(education_text)
        print(f"Extracted {len(education)} education entries")
        for i, edu in enumerate(education):
            print(f"  {i+1}. {edu.degree} from {edu.institution}")
    else:
        print("No education section found!")

if __name__ == "__main__":
    asyncio.run(debug_sections())
