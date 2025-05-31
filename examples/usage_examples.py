"""
Example usage of the Resume Analysis MCP Server
"""

import asyncio
import json
import tempfile
import os
from pathlib import Path

# Add src to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.config import Config
from src.analyzer import ResumeAnalyzer
from src.models import JobRequirement, EducationLevel
from examples.sample_data import (
    SAMPLE_RESUME_TEXT, 
    SAMPLE_RESUME_2_TEXT, 
    SAMPLE_RESUME_3_TEXT,
    SAMPLE_JOB_REQUIREMENTS
)

async def create_sample_files():
    """Create sample resume files for testing"""
    resumes = [
        ("john_doe_resume.txt", SAMPLE_RESUME_TEXT),
        ("sarah_wilson_resume.txt", SAMPLE_RESUME_2_TEXT),
        ("mike_chen_resume.txt", SAMPLE_RESUME_3_TEXT)
    ]
    
    file_paths = []
    temp_dir = tempfile.mkdtemp()
    
    for filename, content in resumes:
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        file_paths.append(file_path)
    
    return file_paths, temp_dir

async def example_single_resume_analysis():
    """Example of analyzing a single resume"""
    print("=" * 60)
    print("EXAMPLE 1: Single Resume Analysis")
    print("=" * 60)
    
    # Setup
    config = Config()
    analyzer = ResumeAnalyzer(config)
    
    # Create sample file
    file_paths, temp_dir = await create_sample_files()
    
    try:
        # Analyze first resume
        result = await analyzer.analyze_single_resume(file_paths[0])
        
        print(f"Candidate: {result.resume.contact_info.name}")
        print(f"Email: {result.resume.contact_info.email}")
        print(f"Overall Score: {result.score.overall_score:.2f}")
        print(f"Experience Years: {result.resume.total_experience_years}")
        print(f"Skills Count: {len(result.resume.skills)}")
        print(f"Processing Time: {result.processing_time:.2f}s")
        print(f"Recommendation: {result.score.recommendation}")
        
    finally:
        # Cleanup
        for file_path in file_paths:
            os.unlink(file_path)
        os.rmdir(temp_dir)

async def example_batch_analysis():
    """Example of batch resume analysis"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Batch Resume Analysis")
    print("=" * 60)
    
    # Setup
    config = Config()
    analyzer = ResumeAnalyzer(config)
    
    # Create sample files
    file_paths, temp_dir = await create_sample_files()
    
    try:
        # Analyze all resumes
        results = await analyzer.analyze_batch_resumes(file_paths)
        
        print(f"Analyzed {len(results)} resumes:")
        print("-" * 40)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.resume.contact_info.name}")
            print(f"   Score: {result.score.overall_score:.2f}")
            print(f"   Experience: {result.resume.total_experience_years} years")
            print(f"   Skills: {len(result.resume.skills)}")
            print()
        
    finally:
        # Cleanup
        for file_path in file_paths:
            os.unlink(file_path)
        os.rmdir(temp_dir)

async def example_job_matching():
    """Example of job matching analysis"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Job Matching Analysis")
    print("=" * 60)
    
    # Setup
    config = Config()
    analyzer = ResumeAnalyzer(config)
    
    # Create job requirements
    job_req = JobRequirement(
        title=SAMPLE_JOB_REQUIREMENTS["title"],
        description=SAMPLE_JOB_REQUIREMENTS["description"],
        required_skills=SAMPLE_JOB_REQUIREMENTS["required_skills"],
        preferred_skills=SAMPLE_JOB_REQUIREMENTS["preferred_skills"],
        required_experience_years=SAMPLE_JOB_REQUIREMENTS["required_experience_years"],
        required_education=EducationLevel(SAMPLE_JOB_REQUIREMENTS["required_education"]),
        location=SAMPLE_JOB_REQUIREMENTS["location"],
        salary_range=SAMPLE_JOB_REQUIREMENTS["salary_range"]
    )
    
    # Create sample files
    file_paths, temp_dir = await create_sample_files()
    
    try:
        # Analyze resumes against job requirements
        results = await analyzer.analyze_batch_resumes(file_paths, job_req)
        sorted_results = analyzer.sort_resumes_by_relevance(results, job_req)
        
        print(f"Job: {job_req.title}")
        print(f"Required Skills: {', '.join(job_req.required_skills[:5])}...")
        print(f"Required Experience: {job_req.required_experience_years} years")
        print("\nCandidate Rankings:")
        print("-" * 50)
        
        for result in sorted_results:
            print(f"Rank {result.ranking}: {result.resume.contact_info.name}")
            print(f"  Overall Score: {result.score.overall_score:.2f}")
            print(f"  Job Match: {result.job_match_percentage:.1f}%")
            print(f"  Matching Skills: {', '.join(result.score.matching_skills[:3])}...")
            if result.score.missing_skills:
                print(f"  Missing Skills: {', '.join(result.score.missing_skills[:3])}...")
            print(f"  Experience Gap: {result.score.experience_gap:.1f} years")
            print()
        
    finally:
        # Cleanup
        for file_path in file_paths:
            os.unlink(file_path)
        os.rmdir(temp_dir)

async def example_filtering():
    """Example of resume filtering"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Resume Filtering")
    print("=" * 60)
    
    # Setup
    config = Config()
    analyzer = ResumeAnalyzer(config)
    
    # Create sample files
    file_paths, temp_dir = await create_sample_files()
    
    try:
        # Analyze all resumes first
        results = await analyzer.analyze_batch_resumes(file_paths)
        
        print(f"Original candidates: {len(results)}")
        
        # Apply filters
        filtered_results = analyzer.filter_resumes_by_criteria(
            results,
            min_score=0.7,
            min_experience=3.0,
            required_skills=["Python", "React"]
        )
        
        print(f"After filtering (score ≥ 0.7, experience ≥ 3 years, has Python & React): {len(filtered_results)}")
        print("\nFiltered candidates:")
        print("-" * 30)
        
        for result in filtered_results:
            print(f"• {result.resume.contact_info.name}")
            print(f"  Score: {result.score.overall_score:.2f}")
            print(f"  Experience: {result.resume.total_experience_years} years")
            candidate_skills = [skill.name for skill in result.resume.skills]
            print(f"  Skills: {', '.join(candidate_skills[:5])}...")
            print()
        
    finally:
        # Cleanup
        for file_path in file_paths:
            os.unlink(file_path)
        os.rmdir(temp_dir)

async def example_comprehensive_report():
    """Example of generating a comprehensive analysis report"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Comprehensive Analysis Report")
    print("=" * 60)
    
    # Setup
    config = Config()
    analyzer = ResumeAnalyzer(config)
    
    # Create job requirements
    job_req = JobRequirement(
        title=SAMPLE_JOB_REQUIREMENTS["title"],
        description=SAMPLE_JOB_REQUIREMENTS["description"],
        required_skills=SAMPLE_JOB_REQUIREMENTS["required_skills"],
        preferred_skills=SAMPLE_JOB_REQUIREMENTS["preferred_skills"],
        required_experience_years=SAMPLE_JOB_REQUIREMENTS["required_experience_years"],
        required_education=EducationLevel(SAMPLE_JOB_REQUIREMENTS["required_education"])
    )
    
    # Create sample files
    file_paths, temp_dir = await create_sample_files()
    
    try:
        # Analyze resumes
        results = await analyzer.analyze_batch_resumes(file_paths, job_req)
        
        # Generate comprehensive report
        report = await analyzer.generate_analysis_report(results, job_req)
        
        print("ANALYSIS SUMMARY")
        print("-" * 20)
        summary = report["analysis_summary"]
        print(f"Total Candidates: {summary['total_candidates']}")
        print(f"Average Score: {summary['average_score']}")
        print(f"Average Experience: {summary['average_experience_years']} years")
        
        print("\nTOP CANDIDATES")
        print("-" * 20)
        for candidate in report["top_candidates"][:3]:
            print(f"{candidate['rank']}. {candidate['name']}")
            print(f"   Score: {candidate['overall_score']}")
            print(f"   Job Match: {candidate['job_match_percentage']}%")
            print(f"   Strengths: {', '.join(candidate['key_strengths'])}")
            print()
        
        print("SKILLS ANALYSIS")
        print("-" * 20)
        for skill_data in report["skills_analysis"]["most_common_skills"][:5]:
            print(f"• {skill_data['skill']}: {skill_data['count']} candidates ({skill_data['percentage']}%)")
        
        print(f"\nTotal unique skills found: {report['skills_analysis']['total_unique_skills']}")
        
        if "ai_insights" in report and report["ai_insights"]:
            print("\nAI INSIGHTS")
            print("-" * 20)
            ai_insights = report["ai_insights"]
            if "recommendations" in ai_insights:
                for rec in ai_insights["recommendations"][:3]:
                    print(f"• {rec}")
        
    finally:
        # Cleanup
        for file_path in file_paths:
            os.unlink(file_path)
        os.rmdir(temp_dir)

async def main():
    """Run all examples"""
    print("Resume Analysis MCP Server - Examples")
    print("=" * 60)
    
    try:
        await example_single_resume_analysis()
        await example_batch_analysis()
        await example_job_matching()
        await example_filtering()
        await example_comprehensive_report()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
