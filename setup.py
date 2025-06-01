#!/usr/bin/env python3
"""
Setup script for resume-mcp
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the root directory
    root_dir = Path(__file__).resolve().parent
    
    # Create necessary directories
    (root_dir / "data").mkdir(exist_ok=True)
    (root_dir / "logs").mkdir(exist_ok=True)
    
    # Check if Python 3.10+ is available
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
        print("Error: Python 3.10 or higher is required.")
        print(f"Current Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        sys.exit(1)
    
    # Check if UV is installed
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        print("UV package manager is already installed.")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Installing UV package manager...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "uv"], check=True)
            print("UV package manager installed successfully.")
        except subprocess.CalledProcessError:
            print("Error: Failed to install UV package manager.")
            sys.exit(1)
    
    # Create and activate virtual environment
    venv_path = root_dir / "venv"
    if not venv_path.exists():
        print("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            print("Virtual environment created successfully.")
        except subprocess.CalledProcessError:
            print("Error: Failed to create virtual environment.")
            sys.exit(1)
    
    # Determine the activation script path based on the platform
    if sys.platform == "win32":
        activate_script = venv_path / "Scripts" / "activate"
        activate_cmd = str(activate_script)
    else:
        activate_script = venv_path / "bin" / "activate"
        activate_cmd = f"source {activate_script}"
    
    # Install dependencies
    print("Installing dependencies...")
    if sys.platform == "win32":
        pip_cmd = str(venv_path / "Scripts" / "uv")
    else:
        pip_cmd = str(venv_path / "bin" / "uv")
    
    try:
        if sys.platform == "win32":
            subprocess.run(
                f"{venv_path}\\Scripts\\uv pip install -r requirements.txt",
                shell=True,
                check=True
            )
        else:
            subprocess.run(
                f"{venv_path}/bin/uv pip install -r requirements.txt",
                shell=True,
                check=True
            )
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies.")
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    env_file = root_dir / ".env"
    env_example = root_dir / ".env.example"
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from .env.example...")
        env_file.write_text(env_example.read_text())
        print(".env file created. Please update it with your API keys.")
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print(f"1. Activate the virtual environment: {activate_cmd}")
    print("2. Update the .env file with your API keys")
    print("3. Run the server: python src/main.py")

if __name__ == "__main__":
    main()
