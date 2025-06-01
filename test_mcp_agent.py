#!/usr/bin/env python3
"""
Test MCP Agent Integration
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_mcp_agent_import():
    """Test if the MCP agent can be imported properly."""
    try:
        import resume_mcp
        print("✅ Successfully imported resume_mcp module")
        
        # Check if agent attribute exists
        if hasattr(resume_mcp, 'agent'):
            print("✅ Found 'agent' attribute in resume_mcp module")
            agent = resume_mcp.agent
            print(f"✅ Agent type: {type(agent)}")
            print(f"✅ Agent name: {getattr(agent, 'name', 'Unknown')}")
            
            # Test server methods
            if hasattr(agent, 'list_tools'):
                print("✅ Agent has list_tools method")
            if hasattr(agent, 'call_tool'):
                print("✅ Agent has call_tool method")
            if hasattr(agent, 'list_resources'):
                print("✅ Agent has list_resources method")
            if hasattr(agent, 'read_resource'):
                print("✅ Agent has read_resource method")
                
            return True
        else:
            print("❌ Missing 'agent' attribute in resume_mcp module")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import resume_mcp: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_individual_components():
    """Test individual component imports."""
    try:
        from resume_mcp import ResumeAnalyzer, JobAnalyzer, ResumeMatcher
        print("✅ Successfully imported analyzer components")
        
        from resume_mcp import StorageManager, FileProcessor
        print("✅ Successfully imported utility components")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import components: {e}")
        return False

if __name__ == "__main__":
    print("Testing Resume MCP Agent Integration...")
    print("=" * 50)
    
    # Test agent import
    agent_test = test_mcp_agent_import()
    print()
    
    # Test component imports
    component_test = test_individual_components()
    print()
    
    if agent_test and component_test:
        print("🎉 All tests passed! MCP Agent is ready for integration.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
