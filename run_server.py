#!/usr/bin/env python3
"""
Resume MCP Server - Standalone runner
"""

import sys
import os
import asyncio
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def run_server():
    """Run the Resume MCP server."""
    try:
        from resume_mcp.mcp_server import main
        await main()
    except ImportError as e:
        print(f"Failed to import MCP server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Starting Resume MCP Server...")
    print("Press Ctrl+C to stop")
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)
