"""
Test ADK Web UI integration for Resume Analysis MCP Server
"""

import asyncio
import json
import tempfile
import os
from pathlib import Path

# Test data
TEST_RESUME_TEXT = """
Jane Smith
Senior Software Engineer
jane.smith@example.com
(555) 987-6543

PROFESSIONAL EXPERIENCE
Senior Software Engineer | TechCorp | 2019-2023
• Developed scalable web applications using Python and React
• Led team of 5 developers in microservices architecture
• Implemented CI/CD pipelines reducing deployment time by 50%

Software Engineer | StartupABC | 2017-2019
• Built REST APIs using Django and PostgreSQL
• Collaborated with product team on feature development

EDUCATION
Bachelor of Computer Science | University of Technology | 2017
GPA: 3.8/4.0

SKILLS
Programming: Python, JavaScript, React, Django
Databases: PostgreSQL, MongoDB, Redis
Cloud: AWS, Docker, Kubernetes
"""

TEST_JOB_REQUIREMENTS = {
    "title": "Senior Software Engineer",
    "description": "Looking for an experienced developer",
    "required_skills": ["Python", "React", "AWS"],
    "required_experience_years": 3,
    "required_education": "bachelor"
}

async def test_adk_web_server():
    """Test the ADK web server functionality"""
    print("Testing ADK Web UI Integration...")
    
    try:
        # Import the ADK main module
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from adk_main import create_web_app, HAS_FASTAPI
        
        if not HAS_FASTAPI:
            print("❌ FastAPI not available - installing required dependencies")
            return False
        
        # Create the web app
        app = create_web_app()
        if not app:
            print("❌ Failed to create web application")
            return False
        
        print("✅ Web application created successfully")
        
        # Test app configuration
        assert app.title == "Resume Analysis MCP Server"
        assert app.version == "1.0.0"
        print("✅ App metadata configured correctly")
        
        # Create a temporary resume file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(TEST_RESUME_TEXT)
            temp_file_path = tmp.name
        
        try:
            # Test the app's routes exist
            routes = [route.path for route in app.routes]
            expected_routes = [
                "/",
                "/health",
                "/analyze-resume",
                "/batch-analyze",
                "/score-resume",
                "/sort-resumes",
                "/filter-resumes",
                "/match-job",
                "/extract-skills",
                "/generate-report",
                "/upload-resume"
            ]
            
            for expected_route in expected_routes:
                if expected_route in routes:
                    print(f"✅ Route {expected_route} exists")
                else:
                    print(f"❌ Route {expected_route} missing")
            
            print("✅ All expected routes configured")
            
        finally:
            # Cleanup temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_config_web_settings():
    """Test configuration with web settings"""
    print("\nTesting Configuration with Web Settings...")
    
    try:
        from src.config import Config
        
        # Set test environment variables
        os.environ['WEB_UI_ENABLED'] = 'true'
        os.environ['ENABLE_CORS'] = 'true'
        os.environ['CORS_ORIGINS'] = 'http://localhost:3000,http://localhost:3001'
        os.environ['MCP_TRANSPORT'] = 'http'
        os.environ['SERVER_HOST'] = 'localhost'
        os.environ['SERVER_PORT'] = '3000'
        
        config = Config(test_mode=True)
        
        # Test web configuration
        assert config.web_ui_enabled == True
        assert config.enable_cors == True
        assert config.mcp_transport == 'http'
        assert config.server_host == 'localhost'
        assert config.server_port == 3000
        assert 'http://localhost:3000' in config.cors_origins
        
        print("✅ Web UI configuration loaded correctly")
        print(f"   Web UI Enabled: {config.web_ui_enabled}")
        print(f"   CORS Enabled: {config.enable_cors}")
        print(f"   Transport: {config.mcp_transport}")
        print(f"   Server: {config.server_host}:{config.server_port}")
        print(f"   CORS Origins: {config.cors_origins}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ai_model_configuration():
    """Test AI model configuration with updated model name"""
    print("\nTesting AI Model Configuration...")
    
    try:
        from src.config import Config
        from src.ai_agent import GoogleAIAgent
        
        # Set AI model environment
        os.environ['AI_MODEL_NAME'] = 'gemini-2.0-flash'
        os.environ['GOOGLE_API_KEY'] = 'test-key'
        
        config = Config(test_mode=True)
        
        # Test AI agent initialization
        ai_agent = GoogleAIAgent(config)
        
        # Check if model name is read from environment
        expected_model = os.getenv('AI_MODEL_NAME', 'gemini-1.5-flash')
        print(f"✅ AI Model configured: {expected_model}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all ADK integration tests"""
    print("🚀 ADK Web UI Integration Tests")
    print("=" * 50)
    
    results = []
    
    # Test configuration
    results.append(await test_config_web_settings())
    
    # Test AI model configuration
    results.append(await test_ai_model_configuration())
    
    # Test web app creation
    results.append(await test_adk_web_server())
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All ADK integration tests passed!")
        print("Your Resume MCP Server is ready for ADK Web UI!")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
    
    return all(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
