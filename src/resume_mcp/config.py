"""
Configuration settings for the resume MCP server
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Base directories
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Server settings
SERVER_HOST = os.environ.get("RESUME_MCP_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("RESUME_MCP_PORT", "8080"))
DEBUG_MODE = os.environ.get("RESUME_MCP_DEBUG", "0") == "1"

# API keys
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Model settings
DEFAULT_MODEL_CONFIG = {
    "model": "gemini-1.5-pro",
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
}

# File upload settings
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = [".pdf", ".doc", ".docx", ".txt", ".rtf"]

def get_model_config() -> Dict[str, Any]:
    """
    Get the model configuration
    
    Returns:
        Dict[str, Any]: Model configuration
    """
    return {
        "model": os.environ.get("RESUME_MCP_MODEL", DEFAULT_MODEL_CONFIG["model"]),
        "temperature": float(os.environ.get("RESUME_MCP_TEMPERATURE", DEFAULT_MODEL_CONFIG["temperature"])),
        "top_p": float(os.environ.get("RESUME_MCP_TOP_P", DEFAULT_MODEL_CONFIG["top_p"])),
        "top_k": int(os.environ.get("RESUME_MCP_TOP_K", DEFAULT_MODEL_CONFIG["top_k"])),
    }

def validate_api_keys() -> bool:
    """
    Validate that required API keys are present
    
    Returns:
        bool: True if all required API keys are present
    """
    if not GOOGLE_API_KEY:
        return False
    return True
