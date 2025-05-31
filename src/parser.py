"""
Resume parsing utilities
"""

import os
import re
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import aiofiles

import PyPDF2
from docx import Document
import pandas as pd
import spacy
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

try:
    from .models import (
        ParsedResume, ContactInfo, Education, Experience, Skill, 
        Project, Certification, EducationLevel, SkillCategory
    )
except ImportError:
    from models import (
        ParsedResume, ContactInfo, Education, Experience, Skill, 
        Project, Certification, EducationLevel, SkillCategory
    )

class ResumeParser:
    """Resume parsing class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_nlp()
        
    def _setup_nlp(self):
        """Setup NLP models and resources"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning("spaCy model not found. Please install with: python -m spacy download en_core_web_sm")
            self.nlp = None
            
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords')
            self.stop_words = set(stopwords.words('english'))
    
    async def parse_file(self, file_path: str) -> ParsedResume:
        """Parse a resume file and extract structured data"""
        try:
            # Extract text from file
            text = await self._extract_text(file_path)
            
            # Parse the extracted text
            resume = await self._parse_text(text, file_path)
            
            return resume
            
        except Exception as e:
            self.logger.error(f"Error parsing file {file_path}: {e}")
            raise
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from various file formats"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return await self._extract_pdf_text(file_path)
        elif extension == '.docx':
            return await self._extract_docx_text(file_path)
        elif extension == '.txt':
            return await self._extract_txt_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            self.logger.error(f"Error extracting PDF text: {e}")
            raise
        return text.strip()
    
    async def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            self.logger.error(f"Error extracting DOCX text: {e}")
            raise
        return text.strip()
    
    async def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                text = await file.read()
        except Exception as e:
            self.logger.error(f"Error extracting TXT text: {e}")
            raise
        return text.strip()
    
    async def _parse_text(self, text: str, file_path: str) -> ParsedResume:
        """Parse resume text and extract structured data"""
        resume = ParsedResume()
        resume.raw_text = text
        resume.file_path = file_path
        
        # Extract different sections
        resume.contact_info = self._extract_contact_info(text)
        resume.summary = self._extract_summary(text)
        resume.education = self._extract_education(text)
        resume.experience = self._extract_experience(text)
        resume.skills = self._extract_skills(text)
        resume.projects = self._extract_projects(text)
        resume.certifications = self._extract_certifications(text)
        resume.languages = self._extract_languages(text)
        
        # Calculate metadata
        resume.total_experience_years = self._calculate_total_experience(resume.experience)
        resume.parsing_confidence = self._calculate_parsing_confidence(resume)
        
        return resume
    
    def _extract_contact_info(self, text: str) -> ContactInfo:
        """Extract contact information from text"""
        contact = ContactInfo()
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact.email = email_match.group()
        
        # Extract phone
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\b\(\d{3}\)\s?\d{3}[-.]?\d{4}\b',
            r'\b\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact.phone = phone_match.group()
                break
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact.linkedin = linkedin_match.group()
        
        # Extract GitHub
        github_pattern = r'github\.com/[\w-]+'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            contact.github = github_match.group()
        
        # Extract name (first line that looks like a name)
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 3 and len(line) < 50 and not any(char.isdigit() for char in line):
                if not re.search(r'@|\.com|\.org|\.net', line):
                    contact.name = line
                    break
        
        return contact
    
    def _extract_summary(self, text: str) -> str:
        """Extract summary/objective section"""
        summary_keywords = ['summary', 'objective', 'profile', 'about']
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in summary_keywords):
                # Extract next few lines as summary
                summary_lines = []
                for j in range(i + 1, min(i + 10, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not self._is_section_header(next_line):
                        summary_lines.append(next_line)
                    elif next_line and self._is_section_header(next_line):
                        break
                return ' '.join(summary_lines)
        
        return ""
    
    def _extract_education(self, text: str) -> List[Education]:
        """Extract education information"""
        education_list = []
        
        # Common degree patterns
        degree_patterns = [
            r'\b(B\.?S\.?|Bachelor|BS|BA|B\.A\.?)\s+(?:of\s+)?(.+?)(?:\n|,|;|$)',
            r'\b(M\.?S\.?|Master|MS|MA|M\.A\.?)\s+(?:of\s+)?(.+?)(?:\n|,|;|$)',
            r'\b(Ph\.?D\.?|PhD|Doctorate)\s+(?:in\s+)?(.+?)(?:\n|,|;|$)',
            r'\b(Associate)\s+(?:of\s+)?(.+?)(?:\n|,|;|$)'
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                education = Education()
                degree_type = match.group(1)
                field = match.group(2).strip()
                
                education.degree = degree_type
                education.field_of_study = field
                
                # Determine education level
                if 'bachelor' in degree_type.lower() or 'b.s' in degree_type.lower():
                    education.level = EducationLevel.BACHELOR
                elif 'master' in degree_type.lower() or 'm.s' in degree_type.lower():
                    education.level = EducationLevel.MASTER
                elif 'phd' in degree_type.lower() or 'doctorate' in degree_type.lower():
                    education.level = EducationLevel.DOCTORATE
                elif 'associate' in degree_type.lower():
                    education.level = EducationLevel.ASSOCIATE
                
                education_list.append(education)
        
        return education_list
    
    def _extract_experience(self, text: str) -> List[Experience]:
        """Extract work experience information"""
        # This is a simplified implementation
        # In a real application, you'd use more sophisticated NLP
        experience_list = []
        
        # Look for experience sections
        exp_keywords = ['experience', 'employment', 'work history', 'career']
        lines = text.split('\n')
        
        in_experience_section = False
        current_exp = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            line_lower = line.lower()
            
            # Check if we're entering experience section
            if any(keyword in line_lower for keyword in exp_keywords):
                in_experience_section = True
                continue
            
            # Check if we're leaving experience section
            if in_experience_section and self._is_section_header(line):
                if current_exp:
                    experience_list.append(current_exp)
                    current_exp = None
                in_experience_section = False
                continue
            
            if in_experience_section:
                # Try to identify job titles and companies
                if self._looks_like_job_title(line):
                    if current_exp:
                        experience_list.append(current_exp)
                    current_exp = Experience()
                    current_exp.position = line
                elif current_exp and self._looks_like_company(line):
                    current_exp.company = line
                elif current_exp and line.startswith('•') or line.startswith('-'):
                    current_exp.responsibilities.append(line[1:].strip())
        
        if current_exp:
            experience_list.append(current_exp)
        
        return experience_list
    
    def _extract_skills(self, text: str) -> List[Skill]:
        """Extract skills from text"""
        skills_list = []
        
        # Common technical skills
        tech_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue',
            'node.js', 'express', 'django', 'flask', 'spring', 'sql',
            'mysql', 'postgresql', 'mongodb', 'redis', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'git', 'jenkins',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn'
        ]
        
        # Common soft skills
        soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving',
            'analytical', 'creative', 'project management', 'time management'
        ]
        
        text_lower = text.lower()
        
        # Extract technical skills
        for skill in tech_skills:
            if skill in text_lower:
                skills_list.append(Skill(
                    name=skill.title(),
                    category=SkillCategory.TECHNICAL
                ))
        
        # Extract soft skills
        for skill in soft_skills:
            if skill in text_lower:
                skills_list.append(Skill(
                    name=skill.title(),
                    category=SkillCategory.SOFT
                ))
        
        return skills_list
    
    def _extract_projects(self, text: str) -> List[Project]:
        """Extract project information"""
        # Simplified implementation
        return []
    
    def _extract_certifications(self, text: str) -> List[Certification]:
        """Extract certification information"""
        # Simplified implementation
        return []
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract language information"""
        # Simplified implementation
        return []
    
    def _is_section_header(self, line: str) -> bool:
        """Check if a line is a section header"""
        section_keywords = [
            'education', 'experience', 'skills', 'projects', 'certifications',
            'languages', 'awards', 'achievements', 'publications', 'references'
        ]
        line_lower = line.lower().strip()
        return any(keyword in line_lower for keyword in section_keywords)
    
    def _looks_like_job_title(self, line: str) -> bool:
        """Check if a line looks like a job title"""
        # Simple heuristic: contains common job title words
        job_words = ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'coordinator']
        return any(word in line.lower() for word in job_words)
    
    def _looks_like_company(self, line: str) -> bool:
        """Check if a line looks like a company name"""
        # Simple heuristic: contains company indicators
        company_indicators = ['inc', 'corp', 'llc', 'ltd', 'company', 'technologies']
        return any(indicator in line.lower() for indicator in company_indicators)
    
    def _calculate_total_experience(self, experience_list: List[Experience]) -> float:
        """Calculate total years of experience"""
        # Simplified calculation
        return len(experience_list) * 2.0  # Assume 2 years per job
    
    def _calculate_parsing_confidence(self, resume: ParsedResume) -> float:
        """Calculate confidence score for parsing quality"""
        confidence = 0.0
        
        # Check presence of key sections
        if resume.contact_info.email:
            confidence += 0.2
        if resume.contact_info.name:
            confidence += 0.2
        if resume.education:
            confidence += 0.2
        if resume.experience:
            confidence += 0.2
        if resume.skills:
            confidence += 0.2
        
        return min(confidence, 1.0)
