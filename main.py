"""
Resume Analysis MCP Server
Main entry point for the MCP server
"""

import asyncio
import logging
import os
from pathlib import Path

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
            logging.FileHandler('resume_mcp_server.log')
        ]
    )

async def main():
    """Main entry point"""
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
        
        logger.info("Starting Resume Analysis MCP Server...")
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
            
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
