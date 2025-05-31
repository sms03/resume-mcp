"""Job description analyzer using NLP techniques."""

import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models.schemas import (
    JobPosting,
    JobRequirement,
    SkillCategory,
)

logger = logging.getLogger(__name__)


class JobAnalyzer:
    """Analyze job descriptions and extract requirements."""
    
    def __init__(self):
        self.skills_database = self._load_skills_database()
        self.requirement_keywords = self._load_requirement_keywords()
        
    async def initialize(self):
        """Initialize the job analyzer."""
        logger.info("Job analyzer initialized successfully")
    
    async def analyze(self, job_text: str, job_title: str, company: str = None) -> JobPosting:
        """Analyze a job description and extract structured requirements."""
        try:
            # Clean and preprocess text
            cleaned_text = self._clean_text(job_text)
            
            # Extract basic info
            if not company:
                company = self._extract_company(cleaned_text)
            location = self._extract_location(cleaned_text)
            
            # Extract requirements
            requirements = self._extract_requirements(cleaned_text)
            
            # Extract preferred skills
            preferred_skills = self._extract_preferred_skills(cleaned_text)
            
            # Extract education requirements
            education_requirements = self._extract_education_requirements(cleaned_text)
            
            # Extract experience range
            experience_range = self._extract_experience_range(cleaned_text)
            
            # Extract salary range
            salary_range = self._extract_salary_range(cleaned_text)
            
            # Extract seniority level
            seniority_level = self._extract_seniority_level(cleaned_text)
            
            # Extract responsibilities
            responsibilities = self._extract_responsibilities(cleaned_text)
            
            # Convert requirements to required_skills dictionary
            required_skills = self._convert_requirements_to_skills_dict(requirements)
            
            return JobPosting(
                title=job_title,
                company=company,
                location=location,
                description=job_text,
                required_skills=required_skills,
                preferred_skills=preferred_skills,
                education_required=education_requirements,
                experience_required=experience_range,
                seniority_level=seniority_level,
                responsibilities=responsibilities,
                created_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error analyzing job description: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\-@.,()\[\]{}/:;\'\"]+', ' ', text)
        return text.strip()
    
    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name from job description."""
        # Look for common patterns
        patterns = [
            r'(?i)(?:company|employer|organization)[\s:]+([A-Za-z\s&.,]+)',
            r'(?i)join\s+([A-Za-z\s&.,]+)',
            r'(?i)about\s+([A-Za-z\s&.,]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                company = match.group(1).strip()
                if len(company) > 3 and len(company) < 50:
                    return company
        
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from job description."""
        # Common location patterns
        patterns = [
            r'(?i)location[\s:]+([A-Za-z\s,]+)',
            r'(?i)based in\s+([A-Za-z\s,]+)',
            r'(?i)([A-Za-z\s]+),\s*[A-Z]{2}(?:\s+\d{5})?',  # City, State format
            r'(?i)remote',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                location = match.group(1) if len(match.groups()) > 0 else match.group(0)
                return location.strip()
        
        return None
    
    def _extract_requirements(self, text: str) -> List[JobRequirement]:
        """Extract job requirements and skills."""
        requirements = []
        
        # Find requirements sections
        req_sections = self._find_requirements_sections(text)
        
        for section in req_sections:
            # Extract skills from this section
            section_requirements = self._extract_skills_from_section(section)
            requirements.extend(section_requirements)
        
        # Remove duplicates
        seen_skills = set()
        unique_requirements = []
        for req in requirements:
            if req.skill.lower() not in seen_skills:
                unique_requirements.append(req)
                seen_skills.add(req.skill.lower())
        
        return unique_requirements
    
    def _find_requirements_sections(self, text: str) -> List[str]:
        """Find sections that contain requirements."""
        sections = []
        
        # Common requirement section headers
        section_patterns = [
            r'(?i)requirements?[:\s]*\n(.*?)(?=\n[A-Z]|\n\n|\Z)',
            r'(?i)qualifications?[:\s]*\n(.*?)(?=\n[A-Z]|\n\n|\Z)',
            r'(?i)skills?[:\s]*\n(.*?)(?=\n[A-Z]|\n\n|\Z)',
            r'(?i)must have[:\s]*\n(.*?)(?=\n[A-Z]|\n\n|\Z)',
            r'(?i)you should have[:\s]*\n(.*?)(?=\n[A-Z]|\n\n|\Z)',
        ]
        
        for pattern in section_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            sections.extend(matches)
        
        # If no specific sections found, use the entire text
        if not sections:
            sections = [text]
        
        return sections
    
    def _extract_skills_from_section(self, section: str) -> List[JobRequirement]:
        """Extract skills and requirements from a text section."""
        requirements = []
        
        # Check each skill in our database
        for skill_name, skill_info in self.skills_database.items():
            if self._skill_mentioned_in_text(skill_name, section):
                importance = self._determine_skill_importance(skill_name, section)
                is_required = self._is_skill_required(skill_name, section)
                min_years = self._extract_minimum_years(skill_name, section)
                
                requirement = JobRequirement(
                    skill=skill_name,
                    category=skill_info['category'],
                    importance=importance,
                    required=is_required,
                    minimum_years=min_years
                )
                requirements.append(requirement)
        
        return requirements
    
    def _skill_mentioned_in_text(self, skill: str, text: str) -> bool:
        """Check if a skill is mentioned in the text."""
        # Create regex pattern for the skill
        pattern = r'\b' + re.escape(skill) + r'\b'
        return bool(re.search(pattern, text, re.IGNORECASE))
    
    def _determine_skill_importance(self, skill: str, text: str) -> float:
        """Determine the importance of a skill based on context."""
        # Higher importance for required skills
        skill_context = self._get_skill_context(skill, text)
        context_lower = skill_context.lower()
        
        if any(keyword in context_lower for keyword in ['required', 'must', 'essential']):
            return 1.0
        elif any(keyword in context_lower for keyword in ['preferred', 'nice', 'bonus']):
            return 0.6
        else:
            return 0.8
    
    def _is_skill_required(self, skill: str, text: str) -> bool:
        """Determine if a skill is required or preferred."""
        skill_context = self._get_skill_context(skill, text)
        context_lower = skill_context.lower()
        
        required_indicators = ['required', 'must', 'essential', 'mandatory']
        return any(indicator in context_lower for indicator in required_indicators)
    
    def _extract_minimum_years(self, skill: str, text: str) -> Optional[int]:
        """Extract minimum years of experience for a skill."""
        skill_context = self._get_skill_context(skill, text)
        
        # Look for patterns like "3+ years", "minimum 2 years"
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience\s*)?(?:in\s*|with\s*)?' + re.escape(skill),
            re.escape(skill) + r'.*?(\d+)\+?\s*years?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, skill_context, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _get_skill_context(self, skill: str, text: str, window: int = 100) -> str:
        """Get context around a skill mention."""
        pattern = r'\b' + re.escape(skill) + r'\b'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            start = max(0, match.start() - window)
            end = min(len(text), match.end() + window)
            return text[start:end]
        
        return ""
    
    def _extract_preferred_skills(self, text: str) -> List[str]:
        """Extract preferred/nice-to-have skills."""
        preferred_skills = []
        
        # Look for preferred skills sections
        preferred_patterns = [
            r'(?i)preferred[\s:]*(.+?)(?=\n[A-Z]|\n\n|\Z)',
            r'(?i)nice.to.have[\s:]*(.+?)(?=\n[A-Z]|\n\n|\Z)',
            r'(?i)bonus[\s:]*(.+?)(?=\n[A-Z]|\n\n|\Z)',
            r'(?i)plus[\s:]*(.+?)(?=\n[A-Z]|\n\n|\Z)',
        ]
        
        for pattern in preferred_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                skills = self._extract_skills_from_text(match)
                preferred_skills.extend(skills)
        
        return list(set(preferred_skills))  # Remove duplicates
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skill names from a text section."""
        skills = []
        for skill_name in self.skills_database.keys():
            if self._skill_mentioned_in_text(skill_name, text):
                skills.append(skill_name)
        return skills
    
    def _extract_education_requirements(self, text: str) -> Optional[str]:
        """Extract education requirements."""
        education_patterns = [
            r'(?i)(?:bachelor|master|phd|doctorate|associate|degree)[\s\']*(?:in\s+)?[\w\s]*',
            r'(?i)(?:b\.?[as]\.?|m\.?[as]\.?|ph\.?d\.?)[\s]*(?:in\s+)?[\w\s]*',
            r'(?i)(?:high\s+school|diploma|ged)',
        ]
        
        education_requirements = []
        for pattern in education_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                clean_match = match.strip()
                if len(clean_match) > 5:
                    education_requirements.append(clean_match)
        
        return list(set(education_requirements))[0] if education_requirements else None
    
    def _extract_experience_range(self, text: str) -> Optional[str]:
        """Extract years of experience required."""
        # Patterns for experience requirements
        patterns = [
            r'(\d+)[-\s]*(?:to|\+)?\s*(?:\d+)?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'minimum\s*(\d+)\s*years?',
            r'at least\s*(\d+)\s*years?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_salary_range(self, text: str) -> Optional[str]:
        """Extract salary range from job description."""
        # Patterns for salary ranges
        patterns = [
            r'\$[\d,]+\s*-\s*\$[\d,]+',
            r'\$[\d,]+k?\s*-\s*\$[\d,]+k?',
            r'[\d,]+k?\s*-\s*[\d,]+k?\s*(?:per\s*year|annually)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_seniority_level(self, text: str) -> Optional[str]:
        """Extract seniority level from job description."""
        seniority_keywords = {
            'entry': ['entry', 'junior', 'associate', 'graduate'],
            'mid': ['mid', 'intermediate', 'experienced'],
            'senior': ['senior', 'lead', 'principal'],
            'executive': ['director', 'manager', 'vp', 'chief'],
        }
        
        text_lower = text.lower()
        
        for level, keywords in seniority_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return level
        
        return None
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities."""
        responsibilities = []
        
        # Look for responsibilities sections
        resp_patterns = [
            r'(?i)responsibilities[\s:]*\n(.*?)(?=\n[A-Z]|\n\n|\Z)',
            r'(?i)duties[\s:]*\n(.*?)(?=\n[A-Z]|\n\n|\Z)',
            r'(?i)you will[\s:]*\n(.*?)(?=\n[A-Z]|\n\n|\Z)',
        ]
        
        for pattern in resp_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                # Split by bullet points or lines
                lines = [line.strip() for line in match.split('\n') if line.strip()]
                responsibilities.extend(lines[:10])  # Limit to 10 responsibilities
        
        return responsibilities
    
    def _convert_requirements_to_skills_dict(self, requirements: List[JobRequirement]) -> Dict[str, List[str]]:
        """Convert JobRequirement list to skills dictionary."""
        skills_dict = {}
        
        for req in requirements:
            category_name = req.category.value if hasattr(req.category, 'value') else str(req.category)
            
            if category_name not in skills_dict:
                skills_dict[category_name] = []
            
            skills_dict[category_name].append(req.skill)
        
        return skills_dict
    
    def _load_skills_database(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive skills database."""
        return {
            # Programming Languages
            'Python': {'category': SkillCategory.TECHNICAL, 'keywords': ['python', 'py']},
            'JavaScript': {'category': SkillCategory.TECHNICAL, 'keywords': ['javascript', 'js', 'es6']},
            'Java': {'category': SkillCategory.TECHNICAL, 'keywords': ['java']},
            'C++': {'category': SkillCategory.TECHNICAL, 'keywords': ['c++', 'cpp']},
            'C#': {'category': SkillCategory.TECHNICAL, 'keywords': ['c#', 'csharp']},
            'Go': {'category': SkillCategory.TECHNICAL, 'keywords': ['golang', 'go']},
            'Rust': {'category': SkillCategory.TECHNICAL, 'keywords': ['rust']},
            'TypeScript': {'category': SkillCategory.TECHNICAL, 'keywords': ['typescript', 'ts']},
            'PHP': {'category': SkillCategory.TECHNICAL, 'keywords': ['php']},
            'Ruby': {'category': SkillCategory.TECHNICAL, 'keywords': ['ruby']},
            'Swift': {'category': SkillCategory.TECHNICAL, 'keywords': ['swift']},
            'Kotlin': {'category': SkillCategory.TECHNICAL, 'keywords': ['kotlin']},
            'R': {'category': SkillCategory.TECHNICAL, 'keywords': ['r language']},
            'MATLAB': {'category': SkillCategory.TECHNICAL, 'keywords': ['matlab']},
            'Scala': {'category': SkillCategory.TECHNICAL, 'keywords': ['scala']},
            
            # Web Technologies
            'React': {'category': SkillCategory.TECHNICAL, 'keywords': ['react', 'reactjs']},
            'Angular': {'category': SkillCategory.TECHNICAL, 'keywords': ['angular', 'angularjs']},
            'Vue.js': {'category': SkillCategory.TECHNICAL, 'keywords': ['vue', 'vuejs']},
            'Node.js': {'category': SkillCategory.TECHNICAL, 'keywords': ['node', 'nodejs']},
            'Express.js': {'category': SkillCategory.TECHNICAL, 'keywords': ['express', 'expressjs']},
            'Django': {'category': SkillCategory.TECHNICAL, 'keywords': ['django']},
            'Flask': {'category': SkillCategory.TECHNICAL, 'keywords': ['flask']},
            'FastAPI': {'category': SkillCategory.TECHNICAL, 'keywords': ['fastapi']},
            'Spring': {'category': SkillCategory.TECHNICAL, 'keywords': ['spring framework']},
            'Laravel': {'category': SkillCategory.TECHNICAL, 'keywords': ['laravel']},
            'Ruby on Rails': {'category': SkillCategory.TECHNICAL, 'keywords': ['rails', 'ror']},
            
            # Databases
            'MySQL': {'category': SkillCategory.TECHNICAL, 'keywords': ['mysql']},
            'PostgreSQL': {'category': SkillCategory.TECHNICAL, 'keywords': ['postgresql', 'postgres']},
            'MongoDB': {'category': SkillCategory.TECHNICAL, 'keywords': ['mongodb', 'mongo']},
            'SQLite': {'category': SkillCategory.TECHNICAL, 'keywords': ['sqlite']},
            'Redis': {'category': SkillCategory.TECHNICAL, 'keywords': ['redis']},
            'Elasticsearch': {'category': SkillCategory.TECHNICAL, 'keywords': ['elasticsearch']},
            'Oracle': {'category': SkillCategory.TECHNICAL, 'keywords': ['oracle database']},
            'SQL Server': {'category': SkillCategory.TECHNICAL, 'keywords': ['sql server', 'mssql']},
            
            # Cloud & DevOps
            'AWS': {'category': SkillCategory.TECHNICAL, 'keywords': ['amazon web services', 'aws']},
            'Azure': {'category': SkillCategory.TECHNICAL, 'keywords': ['microsoft azure', 'azure']},
            'Google Cloud': {'category': SkillCategory.TECHNICAL, 'keywords': ['gcp', 'google cloud platform']},
            'Docker': {'category': SkillCategory.TECHNICAL, 'keywords': ['docker', 'containerization']},
            'Kubernetes': {'category': SkillCategory.TECHNICAL, 'keywords': ['kubernetes', 'k8s']},
            'Jenkins': {'category': SkillCategory.TECHNICAL, 'keywords': ['jenkins']},
            'Terraform': {'category': SkillCategory.TECHNICAL, 'keywords': ['terraform']},
            'Ansible': {'category': SkillCategory.TECHNICAL, 'keywords': ['ansible']},
            'Git': {'category': SkillCategory.TECHNICAL, 'keywords': ['git', 'version control']},
            'GitHub': {'category': SkillCategory.TECHNICAL, 'keywords': ['github']},
            'GitLab': {'category': SkillCategory.TECHNICAL, 'keywords': ['gitlab']},
            
            # Data Science & ML
            'Machine Learning': {'category': SkillCategory.TECHNICAL, 'keywords': ['ml', 'machine learning']},
            'Deep Learning': {'category': SkillCategory.TECHNICAL, 'keywords': ['deep learning', 'neural networks']},
            'TensorFlow': {'category': SkillCategory.TECHNICAL, 'keywords': ['tensorflow']},
            'PyTorch': {'category': SkillCategory.TECHNICAL, 'keywords': ['pytorch']},
            'Pandas': {'category': SkillCategory.TECHNICAL, 'keywords': ['pandas']},
            'NumPy': {'category': SkillCategory.TECHNICAL, 'keywords': ['numpy']},
            'Scikit-learn': {'category': SkillCategory.TECHNICAL, 'keywords': ['sklearn', 'scikit-learn']},
            'Data Analysis': {'category': SkillCategory.TECHNICAL, 'keywords': ['data analysis', 'analytics']},
            'Data Visualization': {'category': SkillCategory.TECHNICAL, 'keywords': ['data viz', 'visualization']},
            'Tableau': {'category': SkillCategory.TECHNICAL, 'keywords': ['tableau']},
            'Power BI': {'category': SkillCategory.TECHNICAL, 'keywords': ['power bi', 'powerbi']},
            
            # Soft Skills
            'Leadership': {'category': SkillCategory.SOFT, 'keywords': ['leadership', 'leading teams']},
            'Communication': {'category': SkillCategory.SOFT, 'keywords': ['communication', 'presentation']},
            'Project Management': {'category': SkillCategory.SOFT, 'keywords': ['project management', 'pm']},
            'Team Collaboration': {'category': SkillCategory.SOFT, 'keywords': ['collaboration', 'teamwork']},
            'Problem Solving': {'category': SkillCategory.SOFT, 'keywords': ['problem solving', 'analytical']},
            'Critical Thinking': {'category': SkillCategory.SOFT, 'keywords': ['critical thinking', 'analysis']},
            'Agile': {'category': SkillCategory.SOFT, 'keywords': ['agile', 'scrum', 'kanban']},
            'Mentoring': {'category': SkillCategory.SOFT, 'keywords': ['mentoring', 'coaching']},
        }
    
    def _load_requirement_keywords(self) -> Dict[str, List[str]]:
        """Load keywords that indicate requirements."""
        return {
            'required': ['required', 'must', 'essential', 'mandatory', 'necessary'],
            'preferred': ['preferred', 'nice to have', 'bonus', 'plus', 'desirable'],
            'experience': ['experience', 'years', 'background', 'expertise'],
            'education': ['degree', 'bachelor', 'master', 'phd', 'education', 'university'],
        }
