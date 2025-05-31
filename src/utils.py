"""
Utility functions for resume analysis
"""

import re
import os
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import mimetypes

def validate_file_path(file_path: str, supported_formats: List[str]) -> bool:
    """Validate if file path exists and has supported format"""
    path = Path(file_path)
    
    if not path.exists():
        return False
    
    if not path.is_file():
        return False
    
    extension = path.suffix.lower().lstrip('.')
    return extension in supported_formats

def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0

def calculate_file_hash(file_path: str) -> str:
    """Calculate MD5 hash of file for deduplication"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except OSError:
        return ""

def normalize_text(text: str) -> str:
    """Normalize text for better parsing"""
    if not text:
        return ""
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove extra newlines
    text = re.sub(r'\n\s*\n', '\n', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_email_from_text(text: str) -> Optional[str]:
    """Extract email address from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group() if match else None

def extract_phone_from_text(text: str) -> Optional[str]:
    """Extract phone number from text"""
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        r'\b\(\d{3}\)\s?\d{3}[-.]?\d{4}\b',
        r'\b\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    
    return None

def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from text"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return urls

def parse_date_string(date_str: str) -> Optional[datetime]:
    """Parse various date string formats"""
    if not date_str:
        return None
    
    # Common date formats
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%B %Y",
        "%b %Y",
        "%Y",
        "%m/%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    return None

def calculate_date_difference_years(start_date: Optional[datetime], end_date: Optional[datetime]) -> float:
    """Calculate difference between dates in years"""
    if not start_date:
        return 0.0
    
    if not end_date:
        end_date = datetime.now()
    
    diff = end_date - start_date
    return diff.days / 365.25

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def detect_file_encoding(file_path: str) -> str:
    """Detect file encoding"""
    try:
        import chardet
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB
            result = chardet.detect(raw_data)
            return result.get('encoding', 'utf-8')
    except ImportError:
        return 'utf-8'  # Default fallback

def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with default value for zero denominator"""
    if denominator == 0:
        return default
    return numerator / denominator

def normalize_skill_name(skill: str) -> str:
    """Normalize skill name for better matching"""
    # Convert to lowercase
    skill = skill.lower().strip()
    
    # Common normalizations
    normalizations = {
        'javascript': ['js', 'java script'],
        'typescript': ['ts'],
        'c++': ['cpp', 'c plus plus'],
        'c#': ['csharp', 'c sharp'],
        'node.js': ['nodejs', 'node'],
        'react.js': ['reactjs'],
        'vue.js': ['vuejs'],
        'angular.js': ['angularjs'],
        'machine learning': ['ml'],
        'artificial intelligence': ['ai'],
        'natural language processing': ['nlp']
    }
    
    for canonical, variants in normalizations.items():
        if skill in variants:
            return canonical
    
    return skill

def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity score"""
    if not text1 or not text2:
        return 0.0
    
    # Convert to sets of words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def extract_years_from_text(text: str) -> List[int]:
    """Extract year values from text"""
    year_pattern = r'\b(19|20)\d{2}\b'
    years = re.findall(year_pattern, text)
    return [int(y) for y in years if y]

def is_valid_email(email: str) -> bool:
    """Validate email address format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def get_mime_type(file_path: str) -> Optional[str]:
    """Get MIME type of file"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type

def create_backup_filename(original_path: str) -> str:
    """Create backup filename with timestamp"""
    path = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{path.stem}_backup_{timestamp}{path.suffix}"

def ensure_directory_exists(directory_path: str) -> bool:
    """Ensure directory exists, create if it doesn't"""
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False

class ProgressTracker:
    """Simple progress tracking utility"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, increment: int = 1):
        """Update progress"""
        self.current += increment
        self.current = min(self.current, self.total)
    
    def get_progress_percentage(self) -> float:
        """Get progress as percentage"""
        if self.total == 0:
            return 100.0
        return (self.current / self.total) * 100
    
    def get_elapsed_time(self) -> timedelta:
        """Get elapsed time"""
        return datetime.now() - self.start_time
    
    def get_eta(self) -> Optional[timedelta]:
        """Get estimated time to completion"""
        if self.current == 0:
            return None
        
        elapsed = self.get_elapsed_time()
        rate = self.current / elapsed.total_seconds()
        remaining = self.total - self.current
        
        if rate > 0:
            eta_seconds = remaining / rate
            return timedelta(seconds=eta_seconds)
        
        return None
    
    def __str__(self) -> str:
        """String representation of progress"""
        percentage = self.get_progress_percentage()
        return f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)"
