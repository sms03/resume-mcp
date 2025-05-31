#!/usr/bin/env python3
"""
Test the mock resume analysis agent
"""

import tempfile
import os
from pathlib import Path

# Create a temporary resume file for testing
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write("""
John Doe Resume
Email: john.doe@example.com
Phone: 555-0123

Experience:
- Software Developer at ABC Company (2020-2023)
- Junior Developer at XYZ Corp (2018-2020)

Skills:
- Python, JavaScript, React, SQL
- Leadership, Communication

Education:
- BS Computer Science, University (2018)
""")
    test_file_path = f.name

try:
    # Test the mock functions
    import sys
    sys.path.append(str(Path(__file__).parent / "agents" / "resume_analysis"))
    
    from agent_mock import analyze_resume, batch_analyze_resumes, score_resume, match_job, extract_skills
    
    print("🧪 Testing Mock Resume Analysis Agent\n")
    
    # Test 1: Single resume analysis
    print("1️⃣ Testing analyze_resume:")
    result = analyze_resume(test_file_path)
    print(f"✅ Result length: {len(result)} characters")
    print(f"📝 Sample: {result[:200]}...\n")
    
    # Test 2: Batch analysis
    print("2️⃣ Testing batch_analyze_resumes:")
    result = batch_analyze_resumes([test_file_path, test_file_path])
    print(f"✅ Result length: {len(result)} characters")
    print(f"📝 Sample: {result[:200]}...\n")
    
    # Test 3: Score resume
    print("3️⃣ Testing score_resume:")
    job_req = '{"title": "Software Developer", "required_skills": ["Python", "JavaScript"]}'
    result = score_resume(test_file_path, job_req)
    print(f"✅ Result length: {len(result)} characters")
    print(f"📝 Sample: {result[:200]}...\n")
    
    # Test 4: Match job
    print("4️⃣ Testing match_job:")
    job_desc = "We are looking for a Python developer with experience in React and SQL."
    result = match_job([test_file_path], job_desc)
    print(f"✅ Result length: {len(result)} characters")
    print(f"📝 Sample: {result[:200]}...\n")
    
    # Test 5: Extract skills
    print("5️⃣ Testing extract_skills:")
    result = extract_skills([test_file_path])
    print(f"✅ Result length: {len(result)} characters")
    print(f"📝 Sample: {result[:200]}...\n")
    
    print("🎉 All mock functions working correctly!")
    
finally:
    # Clean up
    os.unlink(test_file_path)
