#!/usr/bin/env python3
"""
Run script for resume-mcp
"""
import os
import sys
import subprocess
from pathlib import Path
import dotenv

def main():
    # Get the root directory
    root_dir = Path(__file__).resolve().parent
    
    # Load environment variables from .env file
    dotenv_path = root_dir / ".env"
    if dotenv_path.exists():
        dotenv.load_dotenv(dotenv_path)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        venv_path = root_dir / "venv"
        if venv_path.exists():
            print("Virtual environment is not activated.")
            if sys.platform == "win32":
                activate_script = venv_path / "Scripts" / "activate"
                print(f"Please activate it with: {activate_script}")
            else:
                activate_script = venv_path / "bin" / "activate"
                print(f"Please activate it with: source {activate_script}")
            sys.exit(1)
    
    # Check for Google API key
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if not google_api_key or google_api_key == "your_google_api_key_here":
        print("Warning: GOOGLE_API_KEY not set or using default value.")
        print("The application may not function correctly without a valid API key.")
        print("Please update the .env file with your API key.")
    
    # Run the server
    try:
        print("Starting Resume MCP Server...")
        subprocess.run([sys.executable, "src/main.py"], check=True)
    except subprocess.CalledProcessError:
        print("Error: Server failed to start.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
