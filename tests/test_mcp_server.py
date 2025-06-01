"""
Tests for MCP server functionality
"""
from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, AsyncMock
from mcp import ModelContextRequest, Operation
from src.main import app

client = TestClient(app)

@pytest.fixture
def mock_resume_analyzer():
    """Mock the resume analyzer for testing"""
    with patch("resume_mcp.server.resume_analyzer") as mock:
        # Set up mock methods
        mock.analyze_resume = AsyncMock()
        mock.analyze_resume.return_value = {
            "personal_info": {"name": "John Doe"},
            "skills": ["Python", "JavaScript"]
        }
        
        mock.match_resume_to_job = AsyncMock()
        mock.match_resume_to_job.return_value = {
            "match_score": 85,
            "skill_match": {"score": 80}
        }
        
        mock.rank_candidates = AsyncMock()
        mock.rank_candidates.return_value = [
            {"id": "candidate1", "match_score": 85},
            {"id": "candidate2", "match_score": 75}
        ]
        
        yield mock

def test_mcp_agent_description():
    """Test that the MCP server returns an agent description"""
    request = {
        "operation": "DESCRIBE_AGENT"
    }
    response = client.post("/mcp/", json=request)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    
    # Check that it has function definitions
    assert "function_response" in data
    functions = data["function_response"].get("functions", [])
    function_names = [f.get("name") for f in functions]
    assert "analyze_resume" in function_names
    assert "match_resume_to_job" in function_names
    assert "rank_candidates" in function_names

@pytest.mark.asyncio
async def test_analyze_resume_function(mock_resume_analyzer):
    """Test analyze_resume function execution"""
    request = {
        "operation": "EXECUTE_FUNCTION",
        "function_name": "analyze_resume",
        "parameters": {
            "resume_text": "John Doe\nSoftware Engineer\nPython, JavaScript"
        },
        "messages": []
    }
    response = client.post("/mcp/", json=request)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "function_response" in data
    assert "skills" in data["function_response"]
    
    # Check that the analyzer was called
    mock_resume_analyzer.analyze_resume.assert_called_once()

@pytest.mark.asyncio
async def test_match_resume_to_job_function(mock_resume_analyzer):
    """Test match_resume_to_job function execution"""
    request = {
        "operation": "EXECUTE_FUNCTION",
        "function_name": "match_resume_to_job",
        "parameters": {
            "resume_text": "John Doe\nSoftware Engineer\nPython, JavaScript",
            "job_description": "Software Engineer position requiring Python"
        },
        "messages": []
    }
    response = client.post("/mcp/", json=request)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "function_response" in data
    assert "match_score" in data["function_response"]
    
    # Check that the analyzer was called
    mock_resume_analyzer.match_resume_to_job.assert_called_once()

@pytest.mark.asyncio
async def test_rank_candidates_function(mock_resume_analyzer):
    """Test rank_candidates function execution"""
    request = {
        "operation": "EXECUTE_FUNCTION",
        "function_name": "rank_candidates",
        "parameters": {
            "resumes": [
                {"id": "candidate1", "text": "John Doe\nSoftware Engineer\nPython"},
                {"id": "candidate2", "text": "Jane Doe\nDatabase Admin\nSQL"}
            ],
            "job_description": "Software Engineer position requiring Python"
        },
        "messages": []
    }
    response = client.post("/mcp/", json=request)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "function_response" in data
    assert "rankings" in data["function_response"] or isinstance(data["function_response"], list)
    
    # Check that the analyzer was called
    mock_resume_analyzer.rank_candidates.assert_called_once()
