"""
Configuration module for Resume Analysis MCP Server
"""

import os
from typing import Optional, List
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class Config:
    """Configuration class for the resume analysis server"""
    
    # Google Cloud Configuration
    google_cloud_project: Optional[str] = None
    google_application_credentials: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Server Configuration
    mcp_server_port: int = 8000
    log_level: str = "INFO"
    
    # Web Server Configuration (ADK compatibility)
    web_ui_enabled: bool = False
    enable_cors: bool = False
    cors_origins: Optional[List[str]] = None
    mcp_transport: str = "stdio"
    server_host: str = "localhost"
    server_port: int = 3000
    
    # Resume Analysis Settings
    max_file_size_mb: int = 10
    supported_formats: Optional[List[str]] = None
    batch_size_limit: int = 50
    
    # Scoring Weights
    experience_weight: float = 0.3
    education_weight: float = 0.2
    skills_weight: float = 0.4
    achievements_weight: float = 0.1
      # Test mode flag
    test_mode: bool = False
    
    def __post_init__(self):
        """Initialize configuration from environment variables"""
        self.google_cloud_project = os.getenv('GOOGLE_CLOUD_PROJECT') or os.getenv('GOOGLE_PROJECT_ID')
        self.google_application_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        
        self.mcp_server_port = int(os.getenv('MCP_SERVER_PORT', '8000'))
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Web server configuration
        self.web_ui_enabled = os.getenv('WEB_UI_ENABLED', 'false').lower() == 'true'
        self.enable_cors = os.getenv('ENABLE_CORS', 'false').lower() == 'true'
        self.mcp_transport = os.getenv('MCP_TRANSPORT', 'stdio').lower()
        self.server_host = os.getenv('SERVER_HOST', 'localhost')
        self.server_port = int(os.getenv('SERVER_PORT', '3000'))
        
        # Parse CORS origins
        cors_str = os.getenv('CORS_ORIGINS', '')
        self.cors_origins = [origin.strip() for origin in cors_str.split(',') if origin.strip()]
        
        self.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
        self.batch_size_limit = int(os.getenv('BATCH_SIZE_LIMIT', '50'))
        
        # Parse supported formats
        formats_str = os.getenv('SUPPORTED_FORMATS', 'pdf,docx,txt')
        if not formats_str:
            formats_str = os.getenv('SUPPORTED_FILE_TYPES', 'pdf,docx,txt')
        self.supported_formats = [fmt.strip() for fmt in formats_str.split(',')]
        
        # Parse scoring weights
        self.experience_weight = float(os.getenv('EXPERIENCE_WEIGHT', '0.3'))
        self.education_weight = float(os.getenv('EDUCATION_WEIGHT', '0.2'))
        self.skills_weight = float(os.getenv('SKILLS_WEIGHT', '0.4'))
        self.achievements_weight = float(os.getenv('ACHIEVEMENTS_WEIGHT', '0.1'))
          # Alternative weight names from .env
        if os.getenv('DEFAULT_SCORING_WEIGHTS_EXPERIENCE'):
            self.experience_weight = float(os.getenv('DEFAULT_SCORING_WEIGHTS_EXPERIENCE'))
        if os.getenv('DEFAULT_SCORING_WEIGHTS_EDUCATION'):
            self.education_weight = float(os.getenv('DEFAULT_SCORING_WEIGHTS_EDUCATION'))
        if os.getenv('DEFAULT_SCORING_WEIGHTS_SKILLS'):
            self.skills_weight = float(os.getenv('DEFAULT_SCORING_WEIGHTS_SKILLS'))
        if os.getenv('DEFAULT_SCORING_WEIGHTS_ACHIEVEMENTS'):
            self.achievements_weight = float(os.getenv('DEFAULT_SCORING_WEIGHTS_ACHIEVEMENTS'))
        
        # Validate weights sum to 1.0
        total_weight = (self.experience_weight + self.education_weight + 
                       self.skills_weight + self.achievements_weight)
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            raise ValueError(f"Scoring weights must sum to 1.0, got {total_weight}")
    
    def validate(self) -> bool:
        """Validate the configuration"""
        if not self.test_mode and not self.google_cloud_project and not self.google_api_key:
            raise ValueError("Either GOOGLE_CLOUD_PROJECT or GOOGLE_API_KEY must be set")
        
        if self.max_file_size_mb <= 0:
            raise ValueError("MAX_FILE_SIZE_MB must be positive")
        
        if self.batch_size_limit <= 0:
            raise ValueError("BATCH_SIZE_LIMIT must be positive")        
        return True
    
    @property
    def debug(self) -> bool:
        """Get debug mode from environment"""
        return os.getenv('DEBUG', 'false').lower() == 'true'
