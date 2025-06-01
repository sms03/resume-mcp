#!/usr/bin/env python3
"""
Comprehensive MCP Tools Test
"""

import sys
import os
import asyncio
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_mcp_tools():
    """Test all MCP tools are available and functional."""
    
    try:
        from resume_mcp import agent
        print("✅ MCP Agent imported successfully")
        
        # Test list_tools
        print("\n📋 Testing list_tools()...")
        tools = await agent.list_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Test list_resources  
        print("\n📚 Testing list_resources()...")
        resources = await agent.list_resources()
        print(f"✅ Found {len(resources)} resources:")
        for resource in resources:
            print(f"  - {resource.name}: {resource.description}")
        
        # Test specific tool calls with sample data
        print("\n🔧 Testing tool calls...")
        
        # Test analyze_resume with sample data
        sample_resume_text = """
        John Doe
        Software Engineer
        
        Email: john@example.com
        Phone: (555) 123-4567
        
        EXPERIENCE:
        Senior Software Engineer at TechCorp (2020-2023)
        - Developed web applications using Python and React
        - Led team of 5 developers
        
        EDUCATION:
        Bachelor of Computer Science - MIT (2016-2020)
        
        SKILLS:
        Python, JavaScript, React, SQL, AWS
        """
        
        analyze_result = await agent.call_tool(
            "analyze_resume",
            {"resume_text": sample_resume_text}
        )
        print("✅ analyze_resume tool working")
        print(f"  Result: {json.dumps(analyze_result.content[0].text[:100], indent=2)}...")
        
        # Test analyze_job with sample data
        sample_job_text = """
        Software Developer Position
        
        We are looking for a skilled software developer with experience in:
        - Python programming
        - Web development
        - Database management
        - Team collaboration
        
        Requirements:
        - Bachelor's degree in Computer Science
        - 3+ years of experience
        - Strong problem-solving skills
        """
        
        job_result = await agent.call_tool(
            "analyze_job", 
            {"job_description": sample_job_text}
        )
        print("✅ analyze_job tool working")
        
        # Test match_resume_to_job
        match_result = await agent.call_tool(
            "match_resume_to_job",
            {
                "resume_text": sample_resume_text,
                "job_description": sample_job_text
            }
        )
        print("✅ match_resume_to_job tool working")
        print(f"  Match score preview: {json.dumps(match_result.content[0].text[:150], indent=2)}...")
        
        print("\n🎉 All MCP tools are functional!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Resume MCP Tools...")
    print("=" * 50)
    
    success = asyncio.run(test_mcp_tools())
    
    if success:
        print("\n🚀 Resume MCP Agent is fully operational!")
        print("\nAvailable commands:")
        print("  - python run_server.py    # Start MCP server")
        print("  - python test_simple_matching.py  # Test matching")
        print("  - python test_mcp_agent.py       # Test agent import")
    else:
        print("\n⚠️  Some issues detected. Please check the errors above.")
