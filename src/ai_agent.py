"""
Google Agent Development Kit integration for resume analysis
"""

import logging
import asyncio
import os
from typing import List, Dict, Any, Optional
import json

try:
    import google.generativeai as genai
    from google.cloud import aiplatform
    HAS_GOOGLE_AI = True
except ImportError:
    HAS_GOOGLE_AI = False
    logging.warning("Google AI libraries not available. Some features may be limited.")

try:
    from .models import ParsedResume, JobRequirement, ResumeScore, AnalysisResult
    from .config import Config
except ImportError:
    from models import ParsedResume, JobRequirement, ResumeScore, AnalysisResult
    from config import Config

class GoogleAIAgent:
    """Google AI Agent for advanced resume analysis"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._setup_client()
    
    def _setup_client(self):
        """Setup Google AI client"""
        if not HAS_GOOGLE_AI:
            self.logger.warning("Google AI not available")
            self.client = None
            return
        
        try:
            if self.config.google_api_key:
                genai.configure(api_key=self.config.google_api_key)
                # Get model name from environment or use default
                model_name = os.getenv('AI_MODEL_NAME', 'gemini-1.5-flash')
                self.model = genai.GenerativeModel(model_name)
                self.logger.info(f"Google AI configured with API key using model: {model_name}")
            elif self.config.google_cloud_project:
                aiplatform.init(project=self.config.google_cloud_project)
                self.logger.info("Google Cloud AI Platform configured")
            else:
                self.logger.warning("No Google AI credentials configured")
                self.model = None
        except Exception as e:
            self.logger.error(f"Failed to setup Google AI: {e}")
            self.model = None
    
    async def analyze_resume_with_ai(self, resume: ParsedResume, job_req: Optional[JobRequirement] = None) -> Dict[str, Any]:
        """Use Google AI to analyze resume content"""
        if not self.model:
            return self._fallback_analysis(resume, job_req)
        
        try:
            prompt = self._build_analysis_prompt(resume, job_req)
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            # Parse AI response
            analysis = self._parse_ai_response(response.text)
            return analysis
            
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return self._fallback_analysis(resume, job_req)
    
    def _build_analysis_prompt(self, resume: ParsedResume, job_req: Optional[JobRequirement]) -> str:
        """Build prompt for AI analysis"""
        prompt = f"""
        Analyze the following resume and provide a comprehensive evaluation:

        RESUME CONTENT:
        Name: {resume.contact_info.name}
        Email: {resume.contact_info.email}
        
        Summary: {resume.summary}
        
        Education:
        {self._format_education(resume.education)}
        
        Experience:
        {self._format_experience(resume.experience)}
        
        Skills:
        {self._format_skills(resume.skills)}
        
        Raw Text:
        {resume.raw_text[:2000]}...  # Truncate for token limits
        """
        
        if job_req:
            prompt += f"""
            
            JOB REQUIREMENTS:
            Title: {job_req.title}
            Description: {job_req.description}
            Required Skills: {', '.join(job_req.required_skills)}
            Preferred Skills: {', '.join(job_req.preferred_skills)}
            Required Experience: {job_req.required_experience_years} years
            Required Education: {job_req.required_education.value}
            """
        
        prompt += """
        
        Please provide a JSON response with the following structure:
        {
            "overall_score": 0.85,
            "experience_score": 0.80,
            "education_score": 0.90,
            "skills_score": 0.85,
            "achievements_score": 0.75,
            "matching_skills": ["skill1", "skill2"],
            "missing_skills": ["skill3", "skill4"],
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "recommendation": "Detailed recommendation text",
            "confidence": 0.90,
            "job_match_percentage": 85.5,
            "analysis_notes": "Detailed analysis notes"
        }
        
        Provide scores from 0.0 to 1.0, and job_match_percentage from 0 to 100.
        Be thorough in your analysis and provide actionable insights.
        """
        
        return prompt
    
    def _format_education(self, education_list) -> str:
        """Format education list for prompt"""
        if not education_list:
            return "None listed"
        
        formatted = []
        for edu in education_list:
            formatted.append(f"- {edu.degree} in {edu.field_of_study} from {edu.institution}")
        return "\n".join(formatted)
    
    def _format_experience(self, experience_list) -> str:
        """Format experience list for prompt"""
        if not experience_list:
            return "None listed"
        
        formatted = []
        for exp in experience_list:
            formatted.append(f"- {exp.position} at {exp.company}")
            if exp.responsibilities:
                formatted.append(f"  Responsibilities: {'; '.join(exp.responsibilities[:3])}")
        return "\n".join(formatted)
    
    def _format_skills(self, skills_list) -> str:
        """Format skills list for prompt"""
        if not skills_list:
            return "None listed"
        
        skills_by_category = {}
        for skill in skills_list:
            category = skill.category.value
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill.name)
        
        formatted = []
        for category, skills in skills_by_category.items():
            formatted.append(f"{category.title()}: {', '.join(skills)}")
        
        return "\n".join(formatted)
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            self.logger.error(f"Failed to parse AI response: {e}")
            return self._default_analysis()
    
    def _fallback_analysis(self, resume: ParsedResume, job_req: Optional[JobRequirement]) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        self.logger.info("Using fallback analysis (rule-based)")
        
        # Simple rule-based scoring
        analysis = self._default_analysis()
        
        # Calculate basic scores
        analysis["experience_score"] = min(len(resume.experience) * 0.2, 1.0)
        analysis["education_score"] = min(len(resume.education) * 0.3, 1.0)
        analysis["skills_score"] = min(len(resume.skills) * 0.05, 1.0)
        analysis["achievements_score"] = 0.5  # Default
        
        # Calculate overall score
        weights = [
            self.config.experience_weight,
            self.config.education_weight,
            self.config.skills_weight,
            self.config.achievements_weight
        ]
        scores = [
            analysis["experience_score"],
            analysis["education_score"],
            analysis["skills_score"],
            analysis["achievements_score"]
        ]
        
        analysis["overall_score"] = sum(w * s for w, s in zip(weights, scores))
        
        # Extract matching skills if job requirements provided
        if job_req:
            resume_skills = {skill.name.lower() for skill in resume.skills}
            required_skills = {skill.lower() for skill in job_req.required_skills}
            
            analysis["matching_skills"] = list(resume_skills.intersection(required_skills))
            analysis["missing_skills"] = list(required_skills - resume_skills)
            analysis["job_match_percentage"] = (len(analysis["matching_skills"]) / 
                                              max(len(required_skills), 1)) * 100
        
        analysis["recommendation"] = self._generate_basic_recommendation(resume, job_req)
        
        return analysis
    
    def _default_analysis(self) -> Dict[str, Any]:
        """Default analysis structure"""
        return {
            "overall_score": 0.0,
            "experience_score": 0.0,
            "education_score": 0.0,
            "skills_score": 0.0,
            "achievements_score": 0.0,
            "matching_skills": [],
            "missing_skills": [],
            "strengths": [],
            "weaknesses": [],
            "recommendation": "",
            "confidence": 0.5,
            "job_match_percentage": 0.0,
            "analysis_notes": "Basic rule-based analysis"
        }
    
    def _generate_basic_recommendation(self, resume: ParsedResume, job_req: Optional[JobRequirement]) -> str:
        """Generate basic recommendation"""
        recommendations = []
        
        if len(resume.experience) < 2:
            recommendations.append("Consider gaining more work experience")
        
        if len(resume.skills) < 5:
            recommendations.append("Expand technical skills portfolio")
        
        if not resume.education:
            recommendations.append("Consider pursuing formal education or certifications")
        
        if job_req and len(resume.skills) > 0:
            resume_skills = {skill.name.lower() for skill in resume.skills}
            required_skills = {skill.lower() for skill in job_req.required_skills}
            missing = required_skills - resume_skills
            
            if missing:
                recommendations.append(f"Develop skills in: {', '.join(list(missing)[:3])}")
        
        return "; ".join(recommendations) if recommendations else "Strong candidate profile"

    async def generate_resume_insights(self, resumes: List[ParsedResume]) -> Dict[str, Any]:
        """Generate insights across multiple resumes"""
        if not self.model:
            return self._basic_insights(resumes)
        
        try:
            # Create summary of all resumes
            summary_prompt = self._build_batch_analysis_prompt(resumes)
            
            response = await asyncio.to_thread(
                self.model.generate_content, summary_prompt
            )
            
            return self._parse_insights_response(response.text)
            
        except Exception as e:
            self.logger.error(f"Batch insights failed: {e}")
            return self._basic_insights(resumes)
    
    def _build_batch_analysis_prompt(self, resumes: List[ParsedResume]) -> str:
        """Build prompt for batch analysis"""
        prompt = f"""
        Analyze the following {len(resumes)} resumes and provide insights:
        
        """
        
        for i, resume in enumerate(resumes[:10], 1):  # Limit to 10 resumes
            prompt += f"""
            Resume {i}:
            - Name: {resume.contact_info.name}
            - Experience: {len(resume.experience)} positions
            - Education: {len(resume.education)} entries
            - Skills: {len(resume.skills)} skills
            - Total Experience: {resume.total_experience_years} years
            
            """
        
        prompt += """
        Provide a JSON response with:
        {
            "total_candidates": 10,
            "average_experience": 5.2,
            "most_common_skills": ["skill1", "skill2"],
            "education_distribution": {"bachelor": 5, "master": 3},
            "top_performers": [1, 3, 7],
            "recommendations": ["insight1", "insight2"],
            "quality_score": 0.75
        }
        """
        
        return prompt
    
    def _parse_insights_response(self, response_text: str) -> Dict[str, Any]:
        """Parse insights response"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
            else:
                raise ValueError("No valid JSON found")
        except Exception as e:
            self.logger.error(f"Failed to parse insights: {e}")
            return self._basic_insights([])
    
    def _basic_insights(self, resumes: List[ParsedResume]) -> Dict[str, Any]:
        """Generate basic insights without AI"""
        if not resumes:
            return {
                "total_candidates": 0,
                "average_experience": 0,
                "most_common_skills": [],
                "education_distribution": {},
                "top_performers": [],
                "recommendations": ["No resumes to analyze"],
                "quality_score": 0.0
            }
        
        # Calculate basic statistics
        total_experience = sum(r.total_experience_years for r in resumes)
        avg_experience = total_experience / len(resumes)
        
        # Count skills
        skill_counts = {}
        for resume in resumes:
            for skill in resume.skills:
                skill_counts[skill.name] = skill_counts.get(skill.name, 0) + 1
        
        most_common = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Education distribution
        edu_dist = {}
        for resume in resumes:
            for edu in resume.education:
                level = edu.level.value
                edu_dist[level] = edu_dist.get(level, 0) + 1
        
        return {
            "total_candidates": len(resumes),
            "average_experience": round(avg_experience, 1),
            "most_common_skills": [skill for skill, count in most_common],
            "education_distribution": edu_dist,
            "top_performers": list(range(min(3, len(resumes)))),  # Top 3 by index
            "recommendations": [
                f"Average experience is {avg_experience:.1f} years",
                f"Most common skill: {most_common[0][0] if most_common else 'None'}"
            ],
            "quality_score": min(avg_experience / 10, 1.0)  # Normalize to 0-1
        }
