@echo off
REM Run tests for the resume-mcp project

echo Running tests for Resume MCP Agent...
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Virtual environment is not activated.
    echo Please activate the virtual environment first.
    echo.
    echo Example: .\venv\Scripts\activate
    exit /b 1
)

REM Install pytest if not already installed
python -m pip install pytest pytest-cov pytest-asyncio

REM Run the tests with coverage report
python -m pytest tests\ -v --cov=src --cov-report=term-missing

echo.
echo Test run complete.
