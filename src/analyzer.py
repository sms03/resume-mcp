"""
Resume analysis and scoring engine
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import time

try:
    from .models import (
        ParsedResume, JobRequirement, ResumeScore, AnalysisResult,
        SkillCategory, EducationLevel
    )
    from .config import Config
    from .parser import ResumeParser
    from .ai_agent import GoogleAIAgent
except ImportError:
    from models import (
        ParsedResume, JobRequirement, ResumeScore, AnalysisResult,
        SkillCategory, EducationLevel
    )
    from config import Config
    from parser import ResumeParser
    from ai_agent import GoogleAIAgent

class ResumeAnalyzer:
    """Main resume analysis engine"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.parser = ResumeParser()
        self.ai_agent = GoogleAIAgent(config)
    
    async def analyze_single_resume(
        self, 
        file_path: str, 
        job_req: Optional[JobRequirement] = None
    ) -> AnalysisResult:
        """Analyze a single resume file"""
        start_time = time.time()
        
        try:
            # Parse the resume
            resume = await self.parser.parse_file(file_path)
            
            # Get AI analysis
            ai_analysis = await self.ai_agent.analyze_resume_with_ai(resume, job_req)
            
            # Create score object
            score = ResumeScore(
                overall_score=ai_analysis.get("overall_score", 0.0),
                experience_score=ai_analysis.get("experience_score", 0.0),
                education_score=ai_analysis.get("education_score", 0.0),
                skills_score=ai_analysis.get("skills_score", 0.0),
                achievements_score=ai_analysis.get("achievements_score", 0.0),
                matching_skills=ai_analysis.get("matching_skills", []),
                missing_skills=ai_analysis.get("missing_skills", []),
                strengths=ai_analysis.get("strengths", []),
                weaknesses=ai_analysis.get("weaknesses", []),
                recommendation=ai_analysis.get("recommendation", ""),
                confidence=ai_analysis.get("confidence", 0.5)
            )
            
            # Create analysis result
            result = AnalysisResult(
                resume=resume,
                score=score,
                job_match_percentage=ai_analysis.get("job_match_percentage", 0.0),
                analysis_notes=ai_analysis.get("analysis_notes", ""),
                processing_time=time.time() - start_time
            )
            
            self.logger.info(f"Analyzed resume: {resume.contact_info.name} - Score: {score.overall_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing resume {file_path}: {e}")
            raise
    
    async def analyze_batch_resumes(
        self, 
        file_paths: List[str], 
        job_req: Optional[JobRequirement] = None
    ) -> List[AnalysisResult]:
        """Analyze multiple resumes in batch"""
        self.logger.info(f"Starting batch analysis of {len(file_paths)} resumes")
        
        # Limit batch size
        if len(file_paths) > self.config.batch_size_limit:
            self.logger.warning(f"Batch size {len(file_paths)} exceeds limit {self.config.batch_size_limit}")
            file_paths = file_paths[:self.config.batch_size_limit]
        
        # Process in parallel with controlled concurrency
        semaphore = asyncio.Semaphore(5)  # Limit concurrent processing
        
        async def analyze_with_semaphore(file_path):
            async with semaphore:
                return await self.analyze_single_resume(file_path, job_req)
        
        try:
            results = await asyncio.gather(
                *[analyze_with_semaphore(fp) for fp in file_paths],
                return_exceptions=True
            )
            
            # Filter out exceptions and log errors
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to analyze {file_paths[i]}: {result}")
                else:
                    valid_results.append(result)
            
            self.logger.info(f"Successfully analyzed {len(valid_results)}/{len(file_paths)} resumes")
            return valid_results
            
        except Exception as e:
            self.logger.error(f"Batch analysis failed: {e}")
            raise
    
    def score_resume_against_job(
        self, 
        resume: ParsedResume, 
        job_req: JobRequirement
    ) -> ResumeScore:
        """Score a resume against specific job requirements"""
        score = ResumeScore()
        
        # Experience scoring
        exp_score = self._score_experience(resume, job_req)
        score.experience_score = exp_score
        
        # Education scoring
        edu_score = self._score_education(resume, job_req)
        score.education_score = edu_score
        
        # Skills scoring
        skills_data = self._score_skills(resume, job_req)
        score.skills_score = skills_data["score"]
        score.matching_skills = skills_data["matching"]
        score.missing_skills = skills_data["missing"]
        
        # Calculate overall score
        score.overall_score = (
            exp_score * self.config.experience_weight +
            edu_score * self.config.education_weight +
            skills_data["score"] * self.config.skills_weight +
            0.5 * self.config.achievements_weight  # Default achievements score
        )
        
        # Calculate experience gap
        score.experience_gap = max(0, job_req.required_experience_years - resume.total_experience_years)
        
        # Generate recommendation
        score.recommendation = self._generate_recommendation(resume, job_req, score)
        
        return score
    
    def _score_experience(self, resume: ParsedResume, job_req: JobRequirement) -> float:
        """Score experience against job requirements"""
        if job_req.required_experience_years == 0:
            return 1.0
        
        experience_ratio = resume.total_experience_years / job_req.required_experience_years
        
        # Cap at 1.0 but allow bonus for extra experience
        if experience_ratio >= 1.0:
            return min(1.0, 0.8 + (experience_ratio - 1.0) * 0.1)
        else:
            return max(0.0, experience_ratio * 0.8)
    
    def _score_education(self, resume: ParsedResume, job_req: JobRequirement) -> float:
        """Score education against job requirements"""
        if job_req.required_education == EducationLevel.OTHER:
            return 0.8  # Neutral score when no specific education required
        
        if not resume.education:
            return 0.3  # Low score for no education
        
        # Education level hierarchy
        education_levels = {
            EducationLevel.HIGH_SCHOOL: 1,
            EducationLevel.CERTIFICATE: 2,
            EducationLevel.ASSOCIATE: 3,
            EducationLevel.BACHELOR: 4,
            EducationLevel.MASTER: 5,
            EducationLevel.DOCTORATE: 6
        }
        
        required_level = education_levels.get(job_req.required_education, 0)
        
        # Get highest education level from resume
        highest_level = 0
        for edu in resume.education:
            level = education_levels.get(edu.level, 0)
            highest_level = max(highest_level, level)
        
        if highest_level >= required_level:
            # Bonus for higher education
            bonus = min(0.2, (highest_level - required_level) * 0.05)
            return min(1.0, 0.8 + bonus)
        else:
            # Penalty for lower education
            penalty = (required_level - highest_level) * 0.2
            return max(0.0, 0.8 - penalty)
    
    def _score_skills(self, resume: ParsedResume, job_req: JobRequirement) -> Dict[str, Any]:
        """Score skills against job requirements"""
        resume_skills = {skill.name.lower() for skill in resume.skills}
        required_skills = {skill.lower() for skill in job_req.required_skills}
        preferred_skills = {skill.lower() for skill in job_req.preferred_skills}
        
        # Find matching and missing skills
        matching_required = resume_skills.intersection(required_skills)
        missing_required = required_skills - resume_skills
        matching_preferred = resume_skills.intersection(preferred_skills)
        
        # Calculate score
        if not required_skills:
            score = 0.8  # Neutral score when no skills specified
        else:
            required_match_ratio = len(matching_required) / len(required_skills)
            preferred_bonus = len(matching_preferred) * 0.05  # 5% bonus per preferred skill
            score = min(1.0, required_match_ratio * 0.8 + preferred_bonus)
        
        return {
            "score": score,
            "matching": list(matching_required | matching_preferred),
            "missing": list(missing_required)
        }
    
    def _generate_recommendation(
        self, 
        resume: ParsedResume, 
        job_req: JobRequirement, 
        score: ResumeScore
    ) -> str:
        """Generate recommendation based on analysis"""
        recommendations = []
        
        if score.overall_score >= 0.8:
            recommendations.append("Excellent candidate match")
        elif score.overall_score >= 0.6:
            recommendations.append("Good candidate with some gaps")
        else:
            recommendations.append("Candidate needs development")
        
        if score.experience_gap > 0:
            recommendations.append(f"Needs {score.experience_gap:.1f} more years of experience")
        
        if score.missing_skills:
            missing_str = ", ".join(score.missing_skills[:3])
            recommendations.append(f"Should develop skills in: {missing_str}")
        
        if score.education_score < 0.6:
            recommendations.append("Consider additional education or certifications")
        
        return "; ".join(recommendations)
    
    def sort_resumes_by_relevance(
        self, 
        results: List[AnalysisResult], 
        job_req: Optional[JobRequirement] = None
    ) -> List[AnalysisResult]:
        """Sort resumes by relevance and score"""
        if job_req:
            # Sort by job match percentage first, then overall score
            sorted_results = sorted(
                results,
                key=lambda r: (r.job_match_percentage, r.score.overall_score),
                reverse=True
            )
        else:
            # Sort by overall score only
            sorted_results = sorted(
                results,
                key=lambda r: r.score.overall_score,
                reverse=True
            )
        
        # Assign rankings
        for i, result in enumerate(sorted_results, 1):
            result.ranking = i
        
        return sorted_results
    
    def filter_resumes_by_criteria(
        self,
        results: List[AnalysisResult],
        min_score: float = 0.0,
        min_experience: float = 0.0,
        required_skills: Optional[List[str]] = None,
        education_level: Optional[EducationLevel] = None
    ) -> List[AnalysisResult]:
        """Filter resumes by specific criteria"""
        filtered = []
        
        for result in results:
            # Check minimum score
            if result.score.overall_score < min_score:
                continue
            
            # Check minimum experience
            if result.resume.total_experience_years < min_experience:
                continue
            
            # Check required skills
            if required_skills:
                resume_skills = {skill.name.lower() for skill in result.resume.skills}
                required_set = {skill.lower() for skill in required_skills}
                if not required_set.issubset(resume_skills):
                    continue
            
            # Check education level
            if education_level and education_level != EducationLevel.OTHER:
                education_levels = {
                    EducationLevel.HIGH_SCHOOL: 1,
                    EducationLevel.CERTIFICATE: 2,
                    EducationLevel.ASSOCIATE: 3,
                    EducationLevel.BACHELOR: 4,
                    EducationLevel.MASTER: 5,
                    EducationLevel.DOCTORATE: 6
                }
                
                required_level = education_levels.get(education_level, 0)
                max_candidate_level = 0
                
                for edu in result.resume.education:
                    level = education_levels.get(edu.level, 0)
                    max_candidate_level = max(max_candidate_level, level)
                
                if max_candidate_level < required_level:
                    continue
            
            filtered.append(result)
        
        self.logger.info(f"Filtered {len(results)} resumes to {len(filtered)} candidates")
        return filtered
    
    async def generate_analysis_report(
        self, 
        results: List[AnalysisResult],
        job_req: Optional[JobRequirement] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        if not results:
            return {"error": "No results to analyze"}
        
        # Basic statistics
        total_candidates = len(results)
        avg_score = sum(r.score.overall_score for r in results) / total_candidates
        avg_experience = sum(r.resume.total_experience_years for r in results) / total_candidates
        
        # Top candidates (top 20% or minimum 3)
        top_count = max(3, int(total_candidates * 0.2))
        sorted_results = self.sort_resumes_by_relevance(results, job_req)
        top_candidates = sorted_results[:top_count]
        
        # Skill analysis
        all_skills = {}
        for result in results:
            for skill in result.resume.skills:
                all_skills[skill.name] = all_skills.get(skill.name, 0) + 1
        
        most_common_skills = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Education distribution
        education_dist = {}
        for result in results:
            for edu in result.resume.education:
                level = edu.level.value
                education_dist[level] = education_dist.get(level, 0) + 1
        
        # Get AI insights if available
        ai_insights = await self.ai_agent.generate_resume_insights([r.resume for r in results])
        
        report = {
            "analysis_summary": {
                "total_candidates": total_candidates,
                "average_score": round(avg_score, 2),
                "average_experience_years": round(avg_experience, 1),
                "score_distribution": self._calculate_score_distribution(results),
                "analysis_timestamp": datetime.now().isoformat()
            },
            "top_candidates": [
                {
                    "rank": candidate.ranking,
                    "name": candidate.resume.contact_info.name,
                    "email": candidate.resume.contact_info.email,
                    "overall_score": round(candidate.score.overall_score, 2),
                    "job_match_percentage": round(candidate.job_match_percentage, 1),
                    "experience_years": candidate.resume.total_experience_years,
                    "key_strengths": candidate.score.strengths[:3],
                    "recommendation": candidate.score.recommendation
                }
                for candidate in top_candidates
            ],
            "skills_analysis": {
                "most_common_skills": [
                    {"skill": skill, "count": count, "percentage": round(count/total_candidates*100, 1)}
                    for skill, count in most_common_skills
                ],
                "total_unique_skills": len(all_skills)
            },
            "education_distribution": education_dist,
            "ai_insights": ai_insights,
            "job_requirements": {
                "title": job_req.title if job_req else "Not specified",
                "required_skills": job_req.required_skills if job_req else [],
                "required_experience": job_req.required_experience_years if job_req else 0,
                "required_education": job_req.required_education.value if job_req else "not_specified"
            } if job_req else None
        }
        
        return report
    
    def _calculate_score_distribution(self, results: List[AnalysisResult]) -> Dict[str, int]:
        """Calculate score distribution for reporting"""
        distribution = {
            "excellent (0.8-1.0)": 0,
            "good (0.6-0.8)": 0,
            "fair (0.4-0.6)": 0,
            "poor (0.0-0.4)": 0
        }
        
        for result in results:
            score = result.score.overall_score
            if score >= 0.8:
                distribution["excellent (0.8-1.0)"] += 1
            elif score >= 0.6:
                distribution["good (0.6-0.8)"] += 1
            elif score >= 0.4:
                distribution["fair (0.4-0.6)"] += 1
            else:
                distribution["poor (0.0-0.4)"] += 1
        
        return distribution
