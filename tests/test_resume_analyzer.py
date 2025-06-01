"""
Tests for resume analyzer functionality
"""
import json
import pytest
from unittest.mock import AsyncMock, patch
from resume_mcp.resume_analyzer import ResumeAnalyzer

# Sample resume text for testing
SAMPLE_RESUME = """
John Doe
Software Engineer
email@example.com

EDUCATION
University of Technology, BS Computer Science, 2018-2022

EXPERIENCE
Software Engineer, Tech Company, 2022-Present
- Developed web applications using Python and JavaScript
- Implemented machine learning algorithms

SKILLS
Python, JavaScript, Machine Learning, Git
"""

# Sample job description for testing
SAMPLE_JOB = """
Software Engineer Position
Requirements:
- 2+ years of experience in web development
- Python programming skills
- Database knowledge
"""


@pytest.fixture
def mock_agent():
    """Create a mock ADK agent"""
    with patch("google.adk.agents.llm_agent.Agent") as MockAgent:
        mock_agent = AsyncMock()
        mock_response = AsyncMock()
        mock_response.text = json.dumps({
            "personal_info": {"name": "John Doe"},
            "skills": ["Python", "JavaScript", "Machine Learning", "Git"]
        })
        mock_agent.generate_content.return_value = mock_response
        MockAgent.return_value = mock_agent
        yield mock_agent


@pytest.mark.asyncio
async def test_analyze_resume(mock_agent):
    """Test resume analysis functionality"""
    analyzer = ResumeAnalyzer()
    analyzer.agent = mock_agent
    
    result = await analyzer.analyze_resume(SAMPLE_RESUME)
    
    # Check that the agent was called with the right prompt
    mock_agent.generate_content.assert_called_once()
    
    # Check that the result has the expected structure
    assert "personal_info" in result
    assert "skills" in result
    assert "Python" in result["skills"]


@pytest.mark.asyncio
async def test_match_resume_to_job(mock_agent):
    """Test resume-job matching functionality"""
    analyzer = ResumeAnalyzer()
    analyzer.agent = mock_agent
    
    # Set up different response for this specific test
    mock_response = AsyncMock()
    mock_response.text = json.dumps({
        "match_score": 85,
        "skill_match": {
            "score": 90,
            "matched_skills": ["Python"],
            "missing_skills": ["Database"]
        }
    })
    mock_agent.generate_content.return_value = mock_response
    
    result = await analyzer.match_resume_to_job(SAMPLE_RESUME, SAMPLE_JOB)
    
    # Check that the agent was called
    mock_agent.generate_content.assert_called_once()
    
    # Check that the result has the expected structure
    assert "match_score" in result
    assert "skill_match" in result
    assert result["match_score"] == 85


@pytest.mark.asyncio
async def test_rank_candidates(mock_agent):
    """Test candidate ranking functionality"""
    analyzer = ResumeAnalyzer()
    analyzer.agent = mock_agent
    
    # Set up different response for this specific test
    mock_response = AsyncMock()
    mock_response.text = json.dumps({
        "rankings": [
            {"id": "candidate1", "match_score": 85},
            {"id": "candidate2", "match_score": 75}
        ]
    })
    mock_agent.generate_content.return_value = mock_response
    
    resumes = [
        {"id": "candidate1", "text": SAMPLE_RESUME},
        {"id": "candidate2", "text": "Jane Doe\nDatabase Admin\n2 years experience"}
    ]
    
    result = await analyzer.rank_candidates(resumes, SAMPLE_JOB)
    
    # Check that the agent was called
    mock_agent.generate_content.assert_called_once()
    
    # Check that the result has the expected structure
    assert len(result) == 2
    assert result[0]["id"] == "candidate1"
    assert result[0]["match_score"] == 85
