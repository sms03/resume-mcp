#!/usr/bin/env python3
"""
Main entry point for the Resume MCP Server Agent
"""
import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from resume_mcp.server import setup_mcp_routes
from resume_mcp.claude_integration import setup_claude_routes
from resume_mcp.static_routes import setup_static_routes
from resume_mcp.generate_logo import generate_logo
from resume_mcp.config import SERVER_HOST, SERVER_PORT, validate_api_keys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Resume MCP Agent", 
              description="MCP Server for Resume Analysis",
              version="0.1.0")

# Add CORS middleware to allow connections from Claude desktop app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - in production, specify origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup routes
setup_mcp_routes(app)
setup_claude_routes(app)
setup_static_routes(app)

# Generate logo
generate_logo()

# Validate API keys
if not validate_api_keys():
    logger.warning("Missing required API keys. Some features may not work correctly.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting Resume MCP Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
