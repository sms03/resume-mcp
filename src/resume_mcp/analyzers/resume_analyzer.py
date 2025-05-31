"""Resume analyzer using NLP and machine learning techniques."""

import logging
import re
import spacy
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dateutil import parser

from ..models.schemas import (
    ContactInfo,
    Education,
    ResumeData,
    Skill,
    SkillCategory,
    SkillLevel,
    WorkExperience,
)

logger = logging.getLogger(__name__)


class ResumeAnalyzer:
    """Advanced resume analyzer using NLP and pattern matching."""
    
    def __init__(self):
        self.nlp = None
        self.skills_database = self._load_skills_database()
        self.education_patterns = self._load_education_patterns()
        self.experience_patterns = self._load_experience_patterns()
        
    async def initialize(self):
        """Initialize the NLP model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Resume analyzer initialized successfully")
        except OSError:
            logger.warning("spaCy model not found, using basic text processing")
            self.nlp = None
    
    async def analyze(self, text: str, filename: str) -> ResumeData:
        """Analyze a resume text and extract structured data."""
        try:
            # Clean and preprocess text
            cleaned_text = self._clean_text(text)
            
            # Extract contact information
            contact_info = self._extract_contact_info(cleaned_text)
            
            # Extract sections
            sections = self._extract_sections(cleaned_text)
            
            # Extract work experience
            work_experience = self._extract_work_experience(sections.get("experience", ""))
            
            # Extract education
            education = self._extract_education(sections.get("education", ""))
            
            # Extract skills
            skills = self._extract_skills(cleaned_text)
            
            # Extract summary
            summary = self._extract_summary(sections.get("summary", ""))
            
            # Calculate total experience
            total_experience = self._calculate_total_experience(work_experience)
            
            # Extract additional information
            certifications = self._extract_certifications(cleaned_text)
            projects = self._extract_projects(cleaned_text)
            languages = self._extract_languages(cleaned_text)
            
            return ResumeData(
                filename=filename,
                contact_info=contact_info,
                summary=summary,
                skills=skills,
                education=education,
                work_experience=work_experience,
                certifications=certifications,
                projects=projects,
                languages=languages,
                total_experience_years=total_experience,
                raw_text=text,                metadata={
                    "processed_at": datetime.now().isoformat(),
                    "analyzer_version": "1.0.0",
                    "sections_found": list(sections.keys()),
                }
            )
        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text while preserving line structure."""
        # Remove excessive whitespace within lines but preserve newlines
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Clean each line individually
            line = re.sub(r'\s+', ' ', line)  # Multiple spaces to single space
            line = re.sub(r'[^\w\s\-@.,()\[\]{}/:;\'\"]+', ' ', line)  # Remove special chars
            cleaned_lines.append(line.strip())
        
        # Join back with newlines, removing empty lines
        return '\n'.join(line for line in cleaned_lines if line)
    
    def _extract_contact_info(self, text: str) -> ContactInfo:
        """Extract contact information from resume text."""
        contact = ContactInfo()
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact.email = email_match.group()
        
        # Extract phone
        phone_patterns = [
            r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact.phone = phone_match.group()
                break
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact.linkedin = f"https://{linkedin_match.group()}"
          # Extract GitHub
        github_pattern = r'github\.com/[\w\-]+'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            contact.github = f"https://{github_match.group()}"
        
        # Extract name - improved logic
        lines = [line.strip() for line in text.split('\n') if line.strip()][:10]
        
        for line in lines:
            # Skip lines with emails, phones, or common resume keywords
            if (re.search(r'[@\(\)\d]', line) or 
                re.search(r'\b(email|phone|contact|location|address)\b', line, re.IGNORECASE)):
                continue
            
            # Look for potential names (2-4 words, proper capitalization)
            words = line.split()
            if (2 <= len(words) <= 4 and 
                all(word[0].isupper() for word in words if word.isalpha()) and
                not any(keyword in line.lower() for keyword in ['engineer', 'developer', 'manager', 'analyst', 'director', 'specialist'])):
                contact.name = line.strip()
                break
        
        # Fallback: if no name found, try a simpler approach
        if not contact.name:
            for line in lines[:5]:  # Check first 5 lines only
                # Look for capitalized words that could be names
                words = line.strip().split()
                if (len(words) >= 2 and 
                    all(word.isalpha() and word[0].isupper() for word in words[:2])):
                    # This could be a name
                    contact.name = ' '.join(words[:2])
                    break
        
        return contact
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract main sections from resume."""
        sections = {}
        
        # Common section headers - made more flexible
        section_patterns = {
            'summary': r'(?i)^(summary|profile|objective|about|overview)',
            'experience': r'(?i)^(experience|employment|work|professional|career)',
            'education': r'(?i)^(education|academic|qualifications|degree)',
            'skills': r'(?i)^(skills|technical|competencies|technologies)',
            'projects': r'(?i)^(projects|portfolio)',
            'certifications': r'(?i)^(certifications|certificates|licenses)',
        }
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        current_section = None
        current_content = []
        
        for line in lines:
            # Check if line is a section header (standalone line, not too long)
            section_found = None
            if len(line.split()) <= 5:  # More flexible word count
                for section_name, pattern in section_patterns.items():
                    if re.search(pattern, line):
                        section_found = section_name
                        break
            
            if section_found:
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                  # Start new section
                current_section = section_found
                current_content = []
            elif current_section:
                current_content.append(line)
            else:
                # If no section yet, assume it's summary/header content
                if not sections.get('summary'):
                    if 'summary' not in sections:
                        sections['summary'] = line
                    else:
                        sections['summary'] += '\n' + line
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _extract_work_experience(self, experience_text: str) -> List[WorkExperience]:
        """Extract work experience entries."""
        experiences = []
        
        if not experience_text:
            return experiences
        
        # Try multiple splitting strategies
        # Strategy 1: Split by job titles (lines with company patterns)
        lines = [line.strip() for line in experience_text.split('\n') if line.strip()]
        
        current_job = []
        for line in lines:
            # Check if line looks like a new job entry (contains "at" or has dates in parentheses)
            if ((' at ' in line or re.search(r'\(\d{4}[-\s]*\d{4}', line)) and 
                len(line.split()) >= 3 and len(line) < 100):
                # Save previous job if exists
                if current_job:
                    exp = self._parse_work_experience_entry('\n'.join(current_job))
                    if exp:
                        experiences.append(exp)
                current_job = [line]
            else:
                if current_job:  # Only add if we're in a job entry
                    current_job.append(line)
        
        # Don't forget the last job
        if current_job:
            exp = self._parse_work_experience_entry('\n'.join(current_job))
            if exp:
                experiences.append(exp)
        
        # If no experiences found, try simpler approach
        if not experiences:
            # Split by empty lines or bullet points
            entries = re.split(r'\n\s*\n|\n(?=[-*•])', experience_text)
            for entry in entries:
                if len(entry.strip()) > 20:  # Skip short entries
                    exp = self._parse_work_experience_entry(entry.strip())
                    if exp:
                        experiences.append(exp)
        
        return experiences
    
    def _parse_work_experience_entry(self, entry: str) -> Optional[WorkExperience]:
        """Parse a single work experience entry."""
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        
        if len(lines) < 2:
            return None
        
        # Extract job title and company (usually first line)
        first_line = lines[0]
        title_company = self._extract_title_company(first_line)
        
        # Extract dates
        date_info = self._extract_dates(entry)
        
        # Extract description (remaining lines)
        description_lines = lines[1:] if len(lines) > 1 else []
        description = '\n'.join(description_lines)
          # Extract responsibilities and achievements
        responsibilities, achievements = self._parse_responsibilities_achievements(description)
        
        return WorkExperience(
            company=title_company.get('company', ''),
            title=title_company.get('title', ''),
            start_date=date_info.get('start_date'),
            end_date=date_info.get('end_date'),
            duration_months=date_info.get('duration_months'),
            description=description,
            responsibilities=responsibilities,
            achievements=achievements,
            skills_used=self._extract_skills_from_text(description)
        )
    
    def _extract_title_company(self, text: str) -> Dict[str, str]:
        """Extract job title and company from text."""
        # Remove date patterns first to clean the text
        text_clean = re.sub(r'\(\d{4}[-\s]*\d{4}\)', '', text).strip()
        
        # Common patterns: "Title at Company", "Title | Company", "Title - Company"
        patterns = [
            r'(.+?)\s+at\s+(.+?)(?:\s*\(|$)',  # "Title at Company (dates)" or "Title at Company"
            r'(.+?)\s*\|\s*(.+)',
            r'(.+?)\s*-\s*(.+)',
            r'(.+?)\s*,\s*(.+)',        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                company = match.group(2).strip()
                # Remove any remaining date info
                company = re.sub(r'\(\d{4}[-\s]*\d{4}\)', '', company).strip()
                return {'title': title, 'company': company}
        
        # If no pattern matches, assume entire text is the title
        return {'title': text_clean, 'company': ''}
    
    def _extract_dates(self, text: str) -> Dict[str, Any]:
        """Extract date information from text."""
        # Date patterns
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4}|\d{4})',  # MM/DD/YYYY or YYYY
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',  # Month Year
            r'\d{4}',  # Just year
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        # Extract present/current indicators
        has_present = bool(re.search(r'\b(present|current|now)\b', text, re.IGNORECASE))
        
        result = {}
        if dates:
            if len(dates) >= 2:
                result['start_date'] = dates[0]
                result['end_date'] = dates[1] if not has_present else 'Present'
            elif len(dates) == 1:
                if has_present:
                    result['start_date'] = dates[0]
                    result['end_date'] = 'Present'
                else:
                    result['start_date'] = dates[0]
        
        # Calculate duration if possible
        if 'start_date' in result and 'end_date' in result:
            result['duration_months'] = self._calculate_duration_months(
                result['start_date'], result['end_date']
            )
        
        return result
    
    def _calculate_duration_months(self, start_date: str, end_date: str) -> Optional[int]:
        """Calculate duration in months between two dates."""
        try:
            if end_date.lower() in ['present', 'current', 'now']:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            start = parser.parse(start_date)
            end = parser.parse(end_date)
            
            return (end.year - start.year) * 12 + (end.month - start.month)
        except:
            return None
    
    def _parse_responsibilities_achievements(self, text: str) -> Tuple[List[str], List[str]]:
        """Parse responsibilities and achievements from description."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        responsibilities = []
        achievements = []
        
        # Keywords that indicate achievements
        achievement_keywords = ['achieved', 'improved', 'increased', 'reduced', 'led', 'managed', 'developed', 'created']
        
        for line in lines:
            if any(keyword in line.lower() for keyword in achievement_keywords):
                achievements.append(line)
            else:
                responsibilities.append(line)
        
        return responsibilities, achievements
    
    def _extract_education(self, education_text: str) -> List[Education]:
        """Extract education entries."""
        educations = []
        
        # Split by common delimiters
        entries = re.split(r'\n(?=\S)', education_text)
        
        for entry in entries:
            if len(entry.strip()) < 10:  # Skip short entries
                continue
            
            edu = self._parse_education_entry(entry)
            if edu:
                educations.append(edu)
        
        return educations
    
    def _parse_education_entry(self, entry: str) -> Optional[Education]:
        """Parse a single education entry."""
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # Extract degree and field
        degree_info = self._extract_degree_info(entry)
        
        # Extract institution
        institution = self._extract_institution(entry)
        
        # Extract graduation year
        year_match = re.search(r'\b(19|20)\d{2}\b', entry)
        graduation_year = int(year_match.group()) if year_match else None
        
        # Extract GPA
        gpa_match = re.search(r'gpa[:\s]*(\d+\.?\d*)', entry, re.IGNORECASE)
        gpa = float(gpa_match.group(1)) if gpa_match else None
        
        return Education(
            institution=institution,
            degree=degree_info.get('degree', ''),
            field_of_study=degree_info.get('field', ''),
            graduation_year=graduation_year,
            gpa=gpa,
        )
    
    def _extract_degree_info(self, text: str) -> Dict[str, str]:
        """Extract degree and field information."""
        degree_patterns = [
            r'\b(bachelor|master|phd|doctorate|associate|diploma|certificate)\s+(?:of\s+)?(.+?)(?:\s+from|\s+at|\s+-|\s+\d{4}|$)',
            r'\b(b\.?[as]\.?|m\.?[as]\.?|ph\.?d\.?|doctorate|associate)\s+(.+?)(?:\s+from|\s+at|\s+-|\s+\d{4}|$)',
        ]
        
        for pattern in degree_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                degree = match.group(1).strip()
                field = match.group(2).strip() if len(match.groups()) > 1 else ''
                return {'degree': degree, 'field': field}
        
        return {'degree': '', 'field': ''}
    
    def _extract_institution(self, text: str) -> str:
        """Extract institution name from education text."""
        # Look for patterns like "University of ...", "... College", "... Institute"
        institution_patterns = [
            r'university\s+of\s+[\w\s]+',
            r'[\w\s]+\s+university',
            r'[\w\s]+\s+college',
            r'[\w\s]+\s+institute',
            r'[\w\s]+\s+school',
        ]
        
        for pattern in institution_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        # If no pattern matches, return the first line (often the institution)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return lines[0] if lines else ''
    
    def _extract_skills(self, text: str) -> List[Skill]:
        """Extract skills from resume text."""
        skills = []
        found_skills = set()
        
        # Match against skills database
        for skill_name, skill_info in self.skills_database.items():
            if self._skill_mentioned_in_text(skill_name, text):
                if skill_name.lower() not in found_skills:
                    skills.append(Skill(
                        name=skill_name,
                        category=skill_info['category'],
                        level=self._estimate_skill_level(skill_name, text),
                        keywords=skill_info.get('keywords', [])
                    ))
                    found_skills.add(skill_name.lower())
        
        return skills
    
    def _skill_mentioned_in_text(self, skill: str, text: str) -> bool:
        """Check if a skill is mentioned in the text."""
        # Create regex pattern for the skill
        pattern = r'\b' + re.escape(skill) + r'\b'
        return bool(re.search(pattern, text, re.IGNORECASE))
    
    def _estimate_skill_level(self, skill: str, text: str) -> Optional[SkillLevel]:
        """Estimate skill level based on context."""
        skill_context = self._get_skill_context(skill, text)
        
        # Level indicators
        expert_indicators = ['expert', 'advanced', 'lead', 'senior', 'architect']
        intermediate_indicators = ['experienced', 'proficient', 'skilled']
        beginner_indicators = ['basic', 'beginner', 'learning', 'familiar']
        
        context_lower = skill_context.lower()
        
        if any(indicator in context_lower for indicator in expert_indicators):
            return SkillLevel.EXPERT
        elif any(indicator in context_lower for indicator in intermediate_indicators):
            return SkillLevel.INTERMEDIATE
        elif any(indicator in context_lower for indicator in beginner_indicators):
            return SkillLevel.BEGINNER
        
        return None
    
    def _get_skill_context(self, skill: str, text: str, window: int = 50) -> str:
        """Get context around a skill mention."""
        pattern = r'\b' + re.escape(skill) + r'\b'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            start = max(0, match.start() - window)
            end = min(len(text), match.end() + window)
            return text[start:end]
        
        return ""
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills mentioned in a specific text section."""
        skills = []
        for skill_name in self.skills_database.keys():
            if self._skill_mentioned_in_text(skill_name, text):
                skills.append(skill_name)
        return skills
    
    def _extract_summary(self, summary_text: str) -> Optional[str]:
        """Extract and clean summary text."""
        if not summary_text or len(summary_text.strip()) < 20:
            return None
        
        # Clean up the summary
        summary = summary_text.strip()
        # Remove multiple spaces and newlines
        summary = re.sub(r'\s+', ' ', summary)
        
        return summary
    
    def _calculate_total_experience(self, work_experiences: List[WorkExperience]) -> Optional[float]:
        """Calculate total years of experience."""
        total_months = 0
        
        for exp in work_experiences:
            if exp.duration_months:
                total_months += exp.duration_months
        
        return round(total_months / 12, 1) if total_months > 0 else None
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from text."""
        certifications = []
        
        # Common certification patterns
        cert_patterns = [
            r'\b(?:certified|certification)\s+[\w\s]+',
            r'\b[A-Z]{2,}\s+certified',
            r'\b(?:AWS|Azure|Google|Microsoft|Oracle|Cisco|CompTIA)[\s\w]+',
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend([match.strip() for match in matches])
        
        return list(set(certifications))  # Remove duplicates
    
    def _extract_projects(self, text: str) -> List[str]:
        """Extract project names/descriptions."""
        projects = []
        
        # Look for project sections or bullet points with project indicators
        project_patterns = [
            r'project[:\s]+(.+?)(?:\n|$)',
            r'built\s+(.+?)(?:\n|$)',
            r'developed\s+(.+?)(?:\n|$)',
            r'created\s+(.+?)(?:\n|$)',
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            projects.extend([match.strip() for match in matches if len(match.strip()) > 10])
        
        return projects[:10]  # Limit to 10 projects
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract spoken languages."""
        languages = []
        
        # Common languages
        common_languages = [
            'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
            'Chinese', 'Japanese', 'Korean', 'Arabic', 'Hindi', 'Russian',
            'Dutch', 'Swedish', 'Norwegian', 'Danish', 'Finnish'
        ]
        
        for language in common_languages:
            if self._skill_mentioned_in_text(language, text):
                languages.append(language)
        
        return languages
    
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
    
    def _load_education_patterns(self) -> List[str]:
        """Load education-related patterns."""
        return [
            r'\b(?:bachelor|master|phd|doctorate|associate|diploma|certificate)',
            r'\b(?:b\.?[as]\.?|m\.?[as]\.?|ph\.?d\.?)',
            r'\buniversity\b',
            r'\bcollege\b',
            r'\binstitute\b',
            r'\bschool\b',
        ]
    
    def _load_experience_patterns(self) -> List[str]:
        """Load work experience-related patterns."""
        return [
            r'\b(?:developer|engineer|manager|analyst|specialist|consultant)\b',
            r'\b(?:senior|junior|lead|principal|staff)\b',
            r'\b(?:full.time|part.time|contract|internship)\b',
            r'\b(?:years?|months?|yrs?)\s+(?:of\s+)?experience\b',
        ]
