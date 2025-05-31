"""Data models and schemas for the resume MCP agent."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class SkillLevel(str, Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SkillCategory(str, Enum):
    """Skill categories."""
    TECHNICAL = "technical"
    SOFT = "soft"
    LANGUAGE = "language"
    CERTIFICATION = "certification"
    DOMAIN = "domain"


class Skill(BaseModel):
    """Individual skill model."""
    name: str
    category: SkillCategory
    level: Optional[SkillLevel] = None
    years_experience: Optional[int] = None
    keywords: List[str] = Field(default_factory=list)


class Education(BaseModel):
    """Education record model."""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    honors: List[str] = Field(default_factory=list)


class WorkExperience(BaseModel):
    """Work experience model."""
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_months: Optional[int] = None
    description: str
    responsibilities: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    skills_used: List[str] = Field(default_factory=list)


class ContactInfo(BaseModel):
    """Contact information model."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None


class ResumeData(BaseModel):
    """Complete resume data model."""
    id: Optional[str] = None
    filename: str
    contact_info: ContactInfo
    summary: Optional[str] = None
    skills: List[Skill] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    work_experience: List[WorkExperience] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    total_experience_years: Optional[float] = None
    raw_text: str
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JobRequirement(BaseModel):
    """Job requirement model."""
    skill: str
    category: SkillCategory
    importance: float = Field(ge=0, le=1)  # 0-1 scale
    required: bool = False
    minimum_years: Optional[int] = None


class JobPosting(BaseModel):
    """Alternative job posting model for compatibility."""
    id: Optional[str] = None
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: str
    required_skills: Dict[str, List[str]] = Field(default_factory=dict)
    preferred_skills: List[str] = Field(default_factory=list)
    education_required: Optional[str] = None
    experience_required: Optional[str] = None
    seniority_level: Optional[str] = None
    industry: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


# Add alias for compatibility
JobDescription = JobPosting


class MatchScore(BaseModel):
    """Individual matching score components."""
    skills_match: float = Field(ge=0, le=1)
    experience_match: float = Field(ge=0, le=1)
    education_match: float = Field(ge=0, le=1)
    overall_score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)


class SkillMatch(BaseModel):
    """Individual skill matching result."""
    score: float = Field(ge=0, le=100)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    skill_categories_match: Dict[str, float] = Field(default_factory=dict)
    
    # Legacy fields for compatibility
    skill_name: Optional[str] = None
    required: bool = False
    candidate_has: bool = False
    candidate_level: Optional[SkillLevel] = None
    required_level: Optional[SkillLevel] = None
    years_experience: Optional[int] = None
    match_strength: float = Field(default=0, ge=0, le=1)


class ExperienceMatch(BaseModel):
    """Experience matching result."""
    score: float = Field(ge=0, le=100)
    years_experience: float
    required_years: float
    meets_requirements: bool
    seniority_match: float = Field(ge=0, le=100)
    relevant_experience_years: float = 0


class EducationMatch(BaseModel):
    """Education matching result."""
    score: float = Field(ge=0, le=100)
    meets_requirements: bool
    education_level_match: bool
    relevant_education: List[str] = Field(default_factory=list)


class OverallMatch(BaseModel):
    """Overall matching result."""
    score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=100)
    skill_match: Optional[SkillMatch] = None
    experience_match: Optional[ExperienceMatch] = None
    education_match: Optional[EducationMatch] = None
    semantic_score: float = Field(ge=0, le=100)


class MatchResult(BaseModel):
    """Resume-job matching result."""
    resume_id: str
    job_id: str
    resume_name: str
    job_title: str
    match_score: MatchScore
    skill_matches: List[SkillMatch] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    overall_score: float = Field(ge=0, le=1)
    ranking_position: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)


class AnalysisResult(BaseModel):
    """General analysis result model."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    processing_time: Optional[float] = None


class SearchQuery(BaseModel):
    """Search query model."""
    query: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    sort_by: Optional[str] = None
    sort_order: str = "desc"  # asc or desc
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class BatchProcessRequest(BaseModel):
    """Batch processing request model."""
    job_id: str
    resume_ids: List[str]
    options: Dict[str, Any] = Field(default_factory=dict)


class Statistics(BaseModel):
    """System statistics model."""
    total_resumes: int
    total_jobs: int
    total_matches: int
    average_match_score: float
    top_skills: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    processing_stats: Dict[str, Any]
