"""
Quick test to verify ADK Web Server functionality
"""

import asyncio
import json
from adk_main import create_web_app, HAS_FASTAPI

async def test_web_app_creation():
    """Test that we can create the web app successfully"""
    print("🧪 Testing ADK Web App Creation...")
    
    if not HAS_FASTAPI:
        print("❌ FastAPI not available")
        return False
    
    try:
        app = create_web_app()
        if app is None:
            print("❌ Failed to create web app")
            return False
        
        print("✅ Web app created successfully")
        
        # Check if routes are properly configured
        routes = [route.path for route in app.routes]
        expected_routes = [
            "/", "/health", "/analyze-resume", "/batch-analyze", 
            "/score-resume", "/sort-resumes", "/filter-resumes", 
            "/match-job", "/extract-skills", "/generate-report", "/upload-resume"
        ]
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} configured")
            else:
                print(f"❌ Route {route} missing")
                return False
        
        print("✅ All routes properly configured")
        return True
        
    except Exception as e:
        print(f"❌ Error creating web app: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 ADK Web Server Quick Test")
    print("=" * 50)
    
    success = await test_web_app_creation()
    
    print("=" * 50)
    if success:
        print("🎉 ADK Web Server is ready for integration!")
        print("To start the server, run: python adk_main.py")
        print("The server will be available at: http://localhost:3000")
        print("\nAvailable endpoints:")
        print("  GET  /         - Server info and status")
        print("  GET  /health   - Health check")
        print("  POST /analyze-resume - Analyze a single resume")
        print("  POST /batch-analyze  - Analyze multiple resumes")
        print("  POST /score-resume   - Score resume against job requirements")
        print("  POST /sort-resumes   - Sort and rank resumes")
        print("  POST /filter-resumes - Filter resumes by criteria")
        print("  POST /match-job      - Match resumes to job description")
        print("  POST /extract-skills - Extract skills from resume")
        print("  POST /generate-report - Generate analysis report")
        print("  POST /upload-resume  - Upload and analyze resume file")
    else:
        print("❌ ADK Web Server configuration failed")

if __name__ == "__main__":
    asyncio.run(main())
