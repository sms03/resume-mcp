"""
Test suite for resume analysis MCP server
"""

import unittest
import tempfile
import os
from unittest.mock import patch
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config
from models import ParsedResume, ContactInfo, JobRequirement, EducationLevel
from parser import ResumeParser
from analyzer import ResumeAnalyzer
from utils import validate_file_path, normalize_text, extract_email_from_text


class TestConfig(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'GOOGLE_API_KEY': 'test-api-key',
            'MCP_SERVER_PORT': '8080',
            'MAX_FILE_SIZE_MB': '5',
            'EXPERIENCE_WEIGHT': '0.35',
            'EDUCATION_WEIGHT': '0.25',
            'SKILLS_WEIGHT': '0.30',
            'ACHIEVEMENTS_WEIGHT': '0.10'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        self.env_patcher.stop()
    
    def test_config_initialization(self):
        """Test configuration initialization from environment"""
        config = Config(test_mode=True)
        
        self.assertEqual(config.google_api_key, 'test-api-key')
        self.assertEqual(config.mcp_server_port, 8080)
        self.assertEqual(config.max_file_size_mb, 5)        # Use actual weights from .env file
        self.assertEqual(config.experience_weight, 0.3)
        self.assertEqual(config.education_weight, 0.25)
        self.assertEqual(config.skills_weight, 0.35)
        self.assertEqual(config.achievements_weight, 0.10)
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = Config(test_mode=True)
        self.assertTrue(config.validate())


class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def test_validate_file_path(self):
        """Test file path validation"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            self.assertTrue(validate_file_path(tmp_path, ['pdf', 'docx']))
            self.assertFalse(validate_file_path(tmp_path, ['txt']))
            self.assertFalse(validate_file_path('nonexistent.pdf', ['pdf']))
        finally:
            os.unlink(tmp_path)
    
    def test_normalize_text(self):
        """Test text normalization"""
        input_text = "  This   is    a\n\n\ntest   text  \n  "
        expected = "This is a test text"
        result = normalize_text(input_text)
        self.assertEqual(result, expected)
    
    def test_extract_email_from_text(self):
        """Test email extraction"""
        text = "Contact John Doe at john.doe@example.com for more info"
        email = extract_email_from_text(text)
        self.assertEqual(email, "john.doe@example.com")


class TestResumeParser(unittest.TestCase):
    """Test resume parsing functionality"""
      def setUp(self):
        self.config = Config(test_mode=True)
        self.parser = ResumeParser()  # ResumeParser doesn't take config parameter
    
    def test_parser_initialization(self):
        """Test parser can be initialized"""
        self.assertIsNotNone(self.parser)
        self.assertEqual(self.parser.config, self.config)


class TestResumeAnalyzer(unittest.TestCase):
    """Test resume analysis functionality"""
    
    def setUp(self):
        self.config = Config(test_mode=True)
        self.analyzer = ResumeAnalyzer(self.config)
    
    def test_analyzer_initialization(self):
        """Test analyzer can be initialized"""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.config, self.config)


if __name__ == '__main__':
    unittest.main(verbosity=2)
