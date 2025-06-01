"""
Static file serving for the web interface
"""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

def setup_static_routes(app: FastAPI):
    """Setup static file serving for the web interface"""
    
    # Get the directory of this file
    current_dir = Path(__file__).parent.absolute()
    
    # Set up static file serving
    static_dir = current_dir / "static"
    ui_dir = current_dir / "ui"
    
    # Ensure the directories exist
    static_dir.mkdir(exist_ok=True)
    ui_dir.mkdir(exist_ok=True)
    
    # Mount the static directory
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Define routes for HTML files
    @app.get("/ui/", response_class=HTMLResponse)
    async def get_ui_index():
        """Serve the UI index page"""
        index_path = ui_dir / "index.html"
        if index_path.exists():
            with open(index_path, "r") as file:
                return file.read()
        else:
            # Return a simple HTML page if the index.html doesn't exist
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Resume MCP Agent</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 20px;
                        color: #333;
                        max-width: 800px;
                        margin: 0 auto;
                    }
                    h1 {
                        color: #0066cc;
                    }
                    .card {
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 20px;
                        margin-bottom: 20px;
                        background-color: #f9f9f9;
                    }
                    .feature {
                        margin-bottom: 10px;
                    }
                    .feature h3 {
                        margin-bottom: 5px;
                    }
                    pre {
                        background-color: #f0f0f0;
                        padding: 10px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }
                </style>
            </head>
            <body>
                <h1>Resume MCP Agent</h1>
                <div class="card">
                    <p>This is a Model Context Protocol (MCP) server for analyzing resumes and matching them to job descriptions.</p>
                    <p>The server is running and ready to use with Claude desktop app.</p>
                </div>
                
                <div class="card">
                    <h2>Features</h2>
                    <div class="feature">
                        <h3>Resume Analysis</h3>
                        <p>Extract skills, experience, education, and other key information from resumes.</p>
                    </div>
                    <div class="feature">
                        <h3>Job Matching</h3>
                        <p>Compare resumes against job descriptions to determine candidate fit.</p>
                    </div>
                    <div class="feature">
                        <h3>Candidate Ranking</h3>
                        <p>Rank multiple candidates based on their fit for a job position.</p>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Claude Desktop Integration</h2>
                    <p>To use this MCP agent with Claude desktop app:</p>
                    <ol>
                        <li>Open Claude desktop app</li>
                        <li>Go to Settings &gt; Plugins</li>
                        <li>Click "Add Plugin"</li>
                        <li>Enter this server URL: <code>http://localhost:8080/mcp/</code></li>
                    </ol>
                </div>
                
                <div class="card">
                    <h2>API Endpoints</h2>
                    <pre>/mcp/ - MCP protocol endpoint</pre>
                    <pre>/upload-resume/ - Upload resume endpoint</pre>
                    <pre>/upload-job-description/ - Upload job description endpoint</pre>
                </div>
            </body>
            </html>
            """
    
    @app.get("/logo.png")
    async def get_logo():
        """Serve the logo file"""
        logo_path = static_dir / "logo.png"
        if not logo_path.exists():
            # If logo doesn't exist, raise 404
            raise HTTPException(status_code=404, detail="Logo not found")
        return FileResponse(logo_path)
