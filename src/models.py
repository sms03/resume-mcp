"""
Data models for resume analysis
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class EducationLevel(Enum):
    """Education level enumeration"""
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"
    CERTIFICATE = "certificate"
    OTHER = "other"

class SkillCategory(Enum):
    """Skill category enumeration"""
    TECHNICAL = "technical"
    SOFT = "soft"
    LANGUAGE = "language"
    CERTIFICATION = "certification"
    TOOL = "tool"
    FRAMEWORK = "framework"

@dataclass
class ContactInfo:
    """Contact information structure"""
    name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""

@dataclass
class Education:
    """Education entry structure"""
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    level: EducationLevel = EducationLevel.OTHER
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    gpa: Optional[float] = None
    honors: List[str] = field(default_factory=list)

@dataclass
class Experience:
    """Work experience entry structure"""
    company: str = ""
    position: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: str = ""
    responsibilities: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)

@dataclass
class Skill:
    """Skill structure"""
    name: str
    category: SkillCategory
    proficiency_level: Optional[str] = None  # Beginner, Intermediate, Advanced, Expert
    years_experience: Optional[int] = None

@dataclass
class Project:
    """Project structure"""
    name: str = ""
    description: str = ""
    technologies: List[str] = field(default_factory=list)
    url: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

@dataclass
class Certification:
    """Certification structure"""
    name: str = ""
    issuer: str = ""
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    credential_id: str = ""

@dataclass
class ParsedResume:
    """Complete parsed resume structure"""
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    summary: str = ""
    education: List[Education] = field(default_factory=list)
    experience: List[Experience] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    certifications: List[Certification] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    raw_text: str = ""
    file_path: str = ""
    
    # Analysis metadata
    parsing_confidence: float = 0.0
    total_experience_years: float = 0.0
    education_score: float = 0.0
    skills_score: float = 0.0
    parsed_at: datetime = field(default_factory=datetime.now)

@dataclass
class JobRequirement:
    """Job requirement structure"""
    title: str = ""
    description: str = ""
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    required_experience_years: int = 0
    required_education: EducationLevel = EducationLevel.OTHER
    location: str = ""
    salary_range: str = ""

@dataclass
class ResumeScore:
    """Resume scoring result"""
    overall_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    skills_score: float = 0.0
    achievements_score: float = 0.0
    
    # Detailed analysis
    matching_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    experience_gap: float = 0.0
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    
    # Recommendation
    recommendation: str = ""
    confidence: float = 0.0

@dataclass
class AnalysisResult:
    """Complete analysis result"""
    resume: ParsedResume
    score: ResumeScore
    job_match_percentage: float = 0.0
    ranking: int = 0
    analysis_notes: str = ""
    processing_time: float = 0.0
