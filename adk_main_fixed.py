"""
ADK Web UI Compatible Entry Point for Resume Analysis MCP Server
Simplified version with better error handling
"""

import asyncio
import logging
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server

from src.server import ResumeAnalysisServer
from src.config import Config

# Load environment variables
load_dotenv()

def setup_logging():
    """Setup logging configuration"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('resume_mcp_adk.log')
        ]
    )

async def run_mcp_server():
    """Run the standard MCP server (stdio transport)"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize configuration
        config = Config()
        
        # Create the resume analysis server
        resume_server = ResumeAnalysisServer(config)
        
        # Initialize the MCP server
        server = Server("resume-analysis-server")
        
        # Register tools with the server
        await resume_server.register_tools(server)
        
        logger.info("Starting Resume Analysis MCP Server (stdio)...")
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
            
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        raise

async def main():
    """Main entry point - run MCP server in stdio mode"""
    await run_mcp_server()

if __name__ == "__main__":
    asyncio.run(main())
