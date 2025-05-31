"""
Resume matching algorithms for intelligent job-resume compatibility analysis.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

from ..models.schemas import (
    ResumeData, JobDescription, MatchResult, SkillMatch, 
    ExperienceMatch, EducationMatch, OverallMatch
)


class ResumeMatcher:
    """Advanced resume-job matching with multiple scoring algorithms."""
    
    def __init__(self):
        """Initialize the resume matcher with NLP models and vectorizers."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        # Skill importance weights
        self.skill_weights = {
            'programming_languages': 1.5,
            'frameworks_libraries': 1.3,
            'databases': 1.2,
            'cloud_devops': 1.4,
            'data_science': 1.3,
            'soft_skills': 0.8
        }
        
        # Experience level mappings
        self.experience_levels = {
            'entry': (0, 2),
            'junior': (1, 3),
            'mid': (3, 6),
            'senior': (5, 10),
            'lead': (7, 15),
            'executive': (10, 30)
        }
    
    def match_resume_to_job(self, resume: ResumeData, job: JobDescription) -> MatchResult:
        """
        Perform comprehensive matching between resume and job description.
        
        Args:
            resume: Parsed resume data
            job: Parsed job description
            
        Returns:
            MatchResult with detailed scoring and analysis
        """
        # Calculate individual match scores
        skill_match = self._calculate_skill_match(resume, job)
        experience_match = self._calculate_experience_match(resume, job)
        education_match = self._calculate_education_match(resume, job)
        
        # Calculate semantic similarity
        semantic_score = self._calculate_semantic_similarity(resume, job)
        
        # Calculate overall match
        overall_match = self._calculate_overall_match(
            skill_match, experience_match, education_match, semantic_score
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(resume, job, overall_match.score)
        
        return MatchResult(
            job_id=job.id,
            resume_id=resume.id if hasattr(resume, 'id') else None,
            overall_match=overall_match,
            skill_match=skill_match,
            experience_match=experience_match,
            education_match=education_match,
            semantic_similarity=semantic_score,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    def _calculate_skill_match(self, resume: ResumeData, job: JobDescription) -> SkillMatch:
        """Calculate skill matching score between resume and job."""
        resume_skills = set()
        job_skills = set()
        
        # Collect all resume skills
        for skill_category in resume.skills.values():
            resume_skills.update(skill.lower() for skill in skill_category)
        
        # Collect all job skills
        for skill_category in job.required_skills.values():
            job_skills.update(skill.lower() for skill in skill_category)
        for skill_category in job.preferred_skills.values():
            job_skills.update(skill.lower() for skill in skill_category)
        
        # Find matching skills
        matched_skills = resume_skills.intersection(job_skills)
        missing_skills = job_skills - resume_skills
        
        # Calculate weighted score
        total_weight = 0
        matched_weight = 0
        
        for category, skills in job.required_skills.items():
            weight = self.skill_weights.get(category, 1.0)
            category_skills = set(skill.lower() for skill in skills)
            total_weight += len(category_skills) * weight
            matched_in_category = category_skills.intersection(resume_skills)
            matched_weight += len(matched_in_category) * weight
        
        # Add preferred skills with lower weight
        for category, skills in job.preferred_skills.items():
            weight = self.skill_weights.get(category, 1.0) * 0.5
            category_skills = set(skill.lower() for skill in skills)
            total_weight += len(category_skills) * weight
            matched_in_category = category_skills.intersection(resume_skills)
            matched_weight += len(matched_in_category) * weight
        
        score = (matched_weight / total_weight * 100) if total_weight > 0 else 0
        
        return SkillMatch(
            score=min(score, 100),
            matched_skills=list(matched_skills),
            missing_skills=list(missing_skills),
            skill_categories_match=self._calculate_category_matches(resume, job)
        )
    
    def _calculate_experience_match(self, resume: ResumeData, job: JobDescription) -> ExperienceMatch:
        """Calculate experience matching score."""
        # Calculate total years of experience
        total_experience = 0
        if resume.work_experience:
            for exp in resume.work_experience:
                if exp.start_date and exp.end_date:
                    years = (exp.end_date - exp.start_date).days / 365.25
                    total_experience += years
                elif exp.start_date and not exp.end_date:
                    # Current job
                    years = (datetime.now().date() - exp.start_date).days / 365.25
                    total_experience += years
        
        # Extract required experience from job
        required_years = self._extract_experience_years(job.experience_required)
        
        # Calculate score based on experience match
        if required_years == 0:
            experience_score = 100  # No specific requirement
        elif total_experience >= required_years:
            # Bonus for exceeding requirements, but cap at 100
            experience_score = min(100, 80 + (total_experience - required_years) * 5)
        else:
            # Penalty for insufficient experience
            experience_score = max(0, (total_experience / required_years) * 80)
        
        # Check for relevant industry experience
        relevant_experience = self._calculate_relevant_experience(resume, job)
        
        return ExperienceMatch(
            score=experience_score,
            years_experience=total_experience,
            years_required=required_years,
            relevant_experience=relevant_experience,
            seniority_match=self._calculate_seniority_match(total_experience, job.seniority_level)
        )
    
    def _calculate_education_match(self, resume: ResumeData, job: JobDescription) -> EducationMatch:
        """Calculate education matching score."""
        if not job.education_required:
            return EducationMatch(score=100, meets_requirements=True, education_level_match=True)
        
        education_score = 0
        meets_requirements = False
        education_level_match = False
        
        required_level = job.education_required.lower()
        
        if resume.education:
            resume_degrees = [edu.degree.lower() for edu in resume.education if edu.degree]
            
            # Education level hierarchy
            education_hierarchy = {
                'high school': 1,
                'associate': 2,
                'bachelor': 3,
                'master': 4,
                'phd': 5,
                'doctorate': 5
            }
            
            # Get highest education level from resume
            max_resume_level = 0
            for degree in resume_degrees:
                for level_name, level_value in education_hierarchy.items():
                    if level_name in degree:
                        max_resume_level = max(max_resume_level, level_value)
            
            # Get required education level
            required_level_value = 0
            for level_name, level_value in education_hierarchy.items():
                if level_name in required_level:
                    required_level_value = level_value
                    break
            
            if max_resume_level >= required_level_value:
                meets_requirements = True
                education_level_match = True
                education_score = 100
            else:
                education_score = (max_resume_level / required_level_value) * 70
        
        return EducationMatch(
            score=education_score,
            meets_requirements=meets_requirements,
            education_level_match=education_level_match
        )
    
    def _calculate_semantic_similarity(self, resume: ResumeData, job: JobDescription) -> float:
        """Calculate semantic similarity using TF-IDF and cosine similarity."""
        try:
            # Combine resume text
            resume_text = self._combine_resume_text(resume)
            
            # Combine job text
            job_text = self._combine_job_text(job)
            
            # Calculate TF-IDF vectors
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([resume_text, job_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity * 100)
        except Exception as e:
            print(f"Error calculating semantic similarity: {e}")
            return 0.0
    
    def _calculate_overall_match(
        self, 
        skill_match: SkillMatch, 
        experience_match: ExperienceMatch, 
        education_match: EducationMatch, 
        semantic_score: float
    ) -> OverallMatch:
        """Calculate overall match score with weighted components."""
        # Weights for different components
        weights = {
            'skills': 0.4,
            'experience': 0.3,
            'education': 0.15,
            'semantic': 0.15
        }
        
        # Calculate weighted score
        overall_score = (
            skill_match.score * weights['skills'] +
            experience_match.score * weights['experience'] +
            education_match.score * weights['education'] +
            semantic_score * weights['semantic']
        )
        
        # Determine match level
        if overall_score >= 85:
            match_level = "excellent"
        elif overall_score >= 70:
            match_level = "good"
        elif overall_score >= 55:
            match_level = "fair"
        else:
            match_level = "poor"
        
        return OverallMatch(
            score=overall_score,
            match_level=match_level,
            confidence=self._calculate_confidence(skill_match, experience_match, education_match)
        )
    
    def _generate_recommendations(self, resume: ResumeData, job: JobDescription, score: float) -> List[str]:
        """Generate actionable recommendations for improving match."""
        recommendations = []
        
        if score < 70:
            # Skill gap analysis
            job_skills = set()
            for skills in job.required_skills.values():
                job_skills.update(skill.lower() for skill in skills)
            
            resume_skills = set()
            for skills in resume.skills.values():
                resume_skills.update(skill.lower() for skill in skills)
            
            missing_skills = job_skills - resume_skills
            if missing_skills:
                recommendations.append(f"Consider developing skills in: {', '.join(list(missing_skills)[:5])}")
        
        # Experience recommendations
        required_years = self._extract_experience_years(job.experience_required)
        total_experience = sum(
            (exp.end_date - exp.start_date).days / 365.25 if exp.end_date else 
            (datetime.now().date() - exp.start_date).days / 365.25
            for exp in resume.work_experience or []
            if exp.start_date
        )
        
        if total_experience < required_years:
            recommendations.append(f"Gain {required_years - total_experience:.1f} more years of relevant experience")
        
        # Education recommendations
        if job.education_required and not resume.education:
            recommendations.append(f"Consider pursuing {job.education_required} education")
        
        return recommendations
    
    def _extract_experience_years(self, experience_text: str) -> float:
        """Extract years of experience from text."""
        if not experience_text:
            return 0
        
        # Common patterns for experience requirements
        patterns = [
            r'(\d+)[-\s]*(?:to|\+)?\s*(?:\d+)?\s*years?',
            r'(\d+)\s*yrs?',
            r'minimum\s*(\d+)\s*years?',
            r'at least\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, experience_text.lower())
            if match:
                return float(match.group(1))
        
        return 0
    
    def _calculate_category_matches(self, resume: ResumeData, job: JobDescription) -> Dict[str, float]:
        """Calculate match percentage for each skill category."""
        category_matches = {}
        
        for category in job.required_skills.keys():
            job_skills = set(skill.lower() for skill in job.required_skills.get(category, []))
            resume_skills = set(skill.lower() for skill in resume.skills.get(category, []))
            
            if job_skills:
                match_percentage = len(job_skills.intersection(resume_skills)) / len(job_skills) * 100
                category_matches[category] = match_percentage
        
        return category_matches
    
    def _calculate_relevant_experience(self, resume: ResumeData, job: JobDescription) -> float:
        """Calculate years of relevant industry experience."""
        if not resume.work_experience or not job.industry:
            return 0
        
        relevant_years = 0
        job_industry_lower = job.industry.lower()
        
        for exp in resume.work_experience:
            if exp.company and job_industry_lower in exp.company.lower():
                if exp.start_date and exp.end_date:
                    years = (exp.end_date - exp.start_date).days / 365.25
                    relevant_years += years
                elif exp.start_date:
                    years = (datetime.now().date() - exp.start_date).days / 365.25
                    relevant_years += years
        
        return relevant_years
    
    def _calculate_seniority_match(self, years_experience: float, required_seniority: str) -> bool:
        """Check if experience level matches required seniority."""
        if not required_seniority:
            return True
        
        required_range = self.experience_levels.get(required_seniority.lower(), (0, 0))
        return required_range[0] <= years_experience <= required_range[1]
    
    def _combine_resume_text(self, resume: ResumeData) -> str:
        """Combine all resume text for semantic analysis."""
        text_parts = []
        
        # Add work experience descriptions
        if resume.work_experience:
            for exp in resume.work_experience:
                if exp.description:
                    text_parts.append(exp.description)
        
        # Add skills
        for skills in resume.skills.values():
            text_parts.extend(skills)
        
        # Add education
        if resume.education:
            for edu in resume.education:
                if edu.degree:
                    text_parts.append(edu.degree)
                if edu.field_of_study:
                    text_parts.append(edu.field_of_study)
        
        # Add projects
        if resume.projects:
            for project in resume.projects:
                if project.description:
                    text_parts.append(project.description)
        
        return " ".join(text_parts)
    
    def _combine_job_text(self, job: JobDescription) -> str:
        """Combine all job description text for semantic analysis."""
        text_parts = [job.description]
        
        # Add skills
        for skills in job.required_skills.values():
            text_parts.extend(skills)
        for skills in job.preferred_skills.values():
            text_parts.extend(skills)
        
        # Add other fields
        if job.responsibilities:
            text_parts.extend(job.responsibilities)
        
        return " ".join(text_parts)
    
    def _calculate_confidence(
        self, 
        skill_match: SkillMatch, 
        experience_match: ExperienceMatch, 
        education_match: EducationMatch
    ) -> float:
        """Calculate confidence score for the match."""
        # Higher confidence when all components are well-defined
        confidence_factors = []
        
        # Skill confidence
        if len(skill_match.matched_skills) > 0:
            confidence_factors.append(min(len(skill_match.matched_skills) / 5, 1.0))
        else:
            confidence_factors.append(0.3)
        
        # Experience confidence
        if experience_match.years_experience > 0:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.5)
        
        # Education confidence
        if education_match.meets_requirements:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.6)
        
        return sum(confidence_factors) / len(confidence_factors) * 100
