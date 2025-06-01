"""
Claude desktop app integration module for resume-mcp
"""
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel, Field
from resume_mcp.claude_formatter import ClaudeResponseFormatter

logger = logging.getLogger(__name__)

class ClaudeIntegrationMessage(BaseModel):
    """Claude message model"""
    role: str = Field(..., description="The role of the message sender (user or assistant)")
    content: str = Field(..., description="The content of the message")

class ClaudeIntegrationRequest(BaseModel):
    """Claude integration request model"""
    messages: List[ClaudeIntegrationMessage] = Field(..., description="The conversation messages")
    model: Optional[str] = Field(None, description="The model to use")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ClaudeIntegrationResponse(BaseModel):
    """Claude integration response model"""
    role: str = Field("assistant", description="The role of the response")
    content: str = Field(..., description="The response content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

def setup_claude_routes(app: FastAPI):
    """
    Set up Claude-specific routes for the FastAPI app
    
    This ensures compatibility with the Claude desktop app when using our MCP server
    """
    claude_router = APIRouter(prefix="/claude", tags=["Claude Integration"])
    
    @claude_router.post("/")
    async def handle_claude_request(request: ClaudeIntegrationRequest) -> ClaudeIntegrationResponse:
        """
        Handle requests from Claude desktop app
        
        This endpoint adds specific compatibility features for Claude's desktop app when
        connecting to our MCP server.
        """
        try:
            # Extract the last user message
            last_user_message = None
            for msg in reversed(request.messages):
                if msg.role.lower() == "user":
                    last_user_message = msg.content
                    break
            
            if not last_user_message:
                raise ValueError("No user message found in the conversation")
            
            # Process the user message
            response_content = await process_claude_message(last_user_message, request.messages)
            
            # Return the response
            return ClaudeIntegrationResponse(
                content=response_content,
                metadata={"source": "resume-mcp"}
            )
            
        except Exception as e:
            logger.error(f"Error processing Claude request: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(claude_router)

async def process_claude_message(message: str, conversation: List[ClaudeIntegrationMessage]) -> str:
    """
    Process a message from Claude desktop app
    
    This function analyzes the message and determines what operation
    to perform based on the user's request.
    
    Args:
        message (str): The user's message
        conversation (List[ClaudeIntegrationMessage]): The full conversation history
        
    Returns:
        str: The response to send back to Claude
    """
    # Simple keyword-based routing to determine the intent
    message_lower = message.lower()
    
    if any(kw in message_lower for kw in ["analyze resume", "parse resume", "extract from resume"]):
        return """
I'll help you analyze this resume using the Resume MCP Agent.

To proceed, please:
1. Upload the resume file using Claude's file upload feature
2. Once uploaded, ask me to "Analyze this resume"
3. I'll then extract key information like skills, experience, education, etc.

Would you like me to analyze a resume now?
"""
    elif any(kw in message_lower for kw in ["match resume", "compare resume", "fit for job"]):
        return """
I can help you match this resume to a job description using the Resume MCP Agent.

To proceed, please:
1. Upload the resume file using Claude's file upload feature
2. Provide the job description (paste it directly or upload as a file)
3. Ask me to "Match this resume to the job description"
4. I'll evaluate how well the candidate matches the position

Would you like me to match a resume to a job description now?
"""
    elif any(kw in message_lower for kw in ["rank candidates", "compare resumes", "sort applicants"]):
        return """
I can help you rank multiple candidates based on their resumes using the Resume MCP Agent.

To proceed, please:
1. Upload multiple resume files using Claude's file upload feature
2. Provide the job description
3. Ask me to "Rank these candidates for this position"
4. I'll evaluate and rank the candidates based on job fit

Would you like me to rank candidates for a position now?
"""
    else:
        # Generic help message
        return """
I'm the Resume Analysis assistant powered by the Resume MCP Agent. Here's how I can help you:

1. **Analyze Resumes**: Extract skills, experience, education, and other key information
2. **Match to Job Descriptions**: Evaluate how well a candidate matches a job
3. **Rank Candidates**: Compare multiple resumes against a job description

To get started, please tell me what you'd like to do, or upload a resume file.
"""
