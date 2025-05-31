#!/usr/bin/env python3
"""
Test Google AI API connectivity
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    
    # Load environment variables from agent directory
    load_dotenv(Path(__file__).parent / "agents" / "resume_analysis" / ".env")
    
    # Configure API
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No GOOGLE_API_KEY found in environment")
        sys.exit(1)
    
    print(f"✅ Found API key: {api_key[:10]}...")
    
    # Configure genai
    genai.configure(api_key=api_key)
    
    # Test with a simple request
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, can you respond with just 'API working'?")
    
    print(f"✅ API Response: {response.text}")
    print("✅ Google AI API is working correctly!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure google-generativeai is installed: pip install google-generativeai")
except Exception as e:
    print(f"❌ API Error: {e}")
    print("Check your API key and internet connection")
