"""
Resume analyzer using Google ADK
"""
import os
import logging
import json
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from google.adk.agents.llm_agent import Agent
from resume_mcp.prompts import (
    RESUME_ANALYSIS_PROMPT,
    RESUME_JOB_MATCHING_PROMPT,
    CANDIDATE_RANKING_PROMPT
)

logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    """Resume analysis using Google ADK"""
    
    def __init__(self):
        """Initialize the resume analyzer"""
        # Set up Google generative AI
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not found in environment. Some features may not work.")
        else:
            genai.configure(api_key=api_key)
        
        # Initialize ADK agent
        try:
            self.agent = self._setup_agent()
            logger.info("ADK agent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ADK agent: {str(e)}")
            self.agent = None
            
    def _setup_agent(self) -> Agent:
        """Set up the ADK agent"""
        # Create an agent with the new API
        agent = Agent(
            name="ResumeAnalysisAgent",
            description="An agent that analyzes resumes and matches them to job descriptions"
        )
        
        return agent
        
    async def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Analyze a resume to extract key information
        
        Args:
            resume_text (str): The text content of the resume
            
        Returns:
            Dict[str, Any]: Structured resume information
        """
        if not self.agent:
            raise RuntimeError("ADK agent not initialized")
        
        try:
            # Create prompt for resume analysis
            prompt = RESUME_ANALYSIS_PROMPT.format(resume_text=resume_text)
            
            # Get response from agent
            response = await self.agent.generate_content(prompt)
            
            # Parse and validate response
            try:
                result = json.loads(response.text)
                return result
            except json.JSONDecodeError:
                # If not valid JSON, extract structured data manually
                logger.warning("Response was not valid JSON, extracting manually")
                return self._extract_structured_data(response.text)
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            return {
                "error": str(e),
                "resume_text": resume_text[:100] + "..." if len(resume_text) > 100 else resume_text
            }
