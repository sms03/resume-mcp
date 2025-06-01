"""
Custom types for Model Context Protocol implementation
"""
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class Operation(Enum):
    """Operation types for MCP requests"""
    EXECUTE_FUNCTION = "execute_function"
    GET_AGENT_DESCRIPTION = "get_agent_description"

class ModelContextMessage(BaseModel):
    """Message in a Model Context Protocol conversation"""
    role: str = Field(..., description="The role of the message sender (user or assistant)")
    content: str = Field(..., description="The content of the message")
    
    class Config:
        frozen = False

class ModelContextRequest(BaseModel):
    """Request model for Model Context Protocol"""
    operation: Operation = Field(..., description="The operation to perform")
    function_name: Optional[str] = Field(None, description="Name of the function to execute")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters for the function")
    messages: Optional[List[ModelContextMessage]] = Field(None, description="Conversation context messages")

class ModelContextResponse(BaseModel):
    """Response model for Model Context Protocol"""
    content: str = Field(..., description="The response content")
    function_response: Optional[Dict[str, Any]] = Field(None, description="Function execution response data")
    error: Optional[str] = Field(None, description="Error message, if applicable")
