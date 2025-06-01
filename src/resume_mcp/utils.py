"""
Utility functions for resume processing
"""
import os
import io
import logging
from typing import Dict, Any
from pathlib import Path
import pypdf

logger = logging.getLogger(__name__)

def extract_text_from_resume(content: bytes, filename: str) -> str:
    """
    Extract text content from a resume file
    
    Args:
        content (bytes): File content
        filename (str): Original filename
        
    Returns:
        str: Extracted text from the resume
    """
    file_ext = Path(filename).suffix.lower()
    
    try:
        if file_ext == '.pdf':
            return extract_text_from_pdf(content)
        elif file_ext in ['.doc', '.docx']:
            logger.warning("Word document extraction requires additional libraries")
            return "Word document extraction not supported"
        elif file_ext in ['.txt', '.rtf']:
            return content.decode('utf-8', errors='ignore')
        else:
            logger.warning(f"Unsupported file format: {file_ext}")
            return f"Unsupported file format: {file_ext}"
    except Exception as e:
        logger.error(f"Error extracting text from resume: {str(e)}")
        return f"Error extracting text: {str(e)}"

def extract_text_from_pdf(content: bytes) -> str:
    """
    Extract text from PDF content
    
    Args:
        content (bytes): PDF file content
        
    Returns:
        str: Extracted text
    """
    try:
        reader = pypdf.PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise
