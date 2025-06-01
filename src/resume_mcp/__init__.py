"""Resume MCP Agent - AI-powered resume analysis and sorting system."""

__version__ = "0.1.0"
__author__ = "Resume MCP Agent"
__email__ = "agent@example.com"

# Import and expose the MCP server as 'agent' for framework compatibility
from .mcp_server import server as agent

# Export all public components
from .analyzers.resume_analyzer import ResumeAnalyzer
from .analyzers.job_analyzer import JobAnalyzer
from .analyzers.resume_matcher import ResumeMatcher
from .storage.storage_manager import StorageManager
from .utils.file_processor import FileProcessor

__all__ = [
    "agent",
    "ResumeAnalyzer",
    "JobAnalyzer", 
    "ResumeMatcher",
    "StorageManager",
    "FileProcessor"
]
