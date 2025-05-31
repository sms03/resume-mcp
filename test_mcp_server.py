"""Test script for the Resume MCP server."""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from resume_mcp.mcp_server import main


async def test_server():
    """Test the MCP server initialization."""
    try:
        print("Testing Resume MCP server initialization...")
        
        # This would normally start the server, but we'll test just the initialization
        from resume_mcp.analyzers.resume_analyzer import ResumeAnalyzer
        from resume_mcp.analyzers.job_analyzer import JobAnalyzer
        from resume_mcp.analyzers.resume_matcher import ResumeMatcher
        from resume_mcp.storage.storage_manager import StorageManager
        from resume_mcp.utils.file_processor import FileProcessor
        
        print("✓ All imports successful")
        
        # Test individual components
        print("Testing individual components...")
        
        # Test Resume Analyzer
        resume_analyzer = ResumeAnalyzer()
        await resume_analyzer.initialize()
        print("✓ Resume Analyzer initialized")
        
        # Test Job Analyzer  
        job_analyzer = JobAnalyzer()
        await job_analyzer.initialize()
        print("✓ Job Analyzer initialized")
        
        # Test Resume Matcher
        resume_matcher = ResumeMatcher()
        print("✓ Resume Matcher initialized")
        
        # Test Storage Manager
        storage_manager = StorageManager("test_resume_mcp.db")
        print("✓ Storage Manager initialized")
        
        # Test File Processor
        file_processor = FileProcessor()
        print("✓ File Processor initialized")
        
        print("\n🎉 All components initialized successfully!")
        print("The Resume MCP server is ready to run.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_server())
    if success:
        print("\n✅ Resume MCP server test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Resume MCP server test failed!")
        sys.exit(1)
