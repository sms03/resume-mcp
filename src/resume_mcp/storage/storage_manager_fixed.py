"""
Storage manager for persisting resumes, job descriptions, and match results.
"""

import json
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import uuid

from ..models.schemas import ResumeData, JobPosting, MatchResult


class StorageManager:
    """Handles data persistence for the resume MCP agent."""
    
    def __init__(self, db_path: str = "resume_mcp.db"):
        """Initialize storage manager with database connection."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def initialize_database(self) -> None:
        """Public method to initialize or reinitialize the database."""
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create resumes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    id TEXT PRIMARY KEY,
                    filename TEXT,
                    content_hash TEXT UNIQUE,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create job descriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    company TEXT,
                    content_hash TEXT UNIQUE,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create match results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS match_results (
                    id TEXT PRIMARY KEY,
                    resume_id TEXT,
                    job_id TEXT,
                    overall_score REAL,
                    match_level TEXT,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (resume_id) REFERENCES resumes (id),
                    FOREIGN KEY (job_id) REFERENCES job_descriptions (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_resumes_hash ON resumes (content_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_hash ON job_descriptions (content_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_resume ON match_results (resume_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_job ON match_results (job_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_score ON match_results (overall_score)")
            
            conn.commit()
    
    def save_resume(self, resume_data: ResumeData, filename: Optional[str] = None) -> str:
        """
        Save resume data to database.
        
        Args:
            resume_data: Parsed resume data
            filename: Original filename (optional)
            
        Returns:
            Resume ID
        """
        # Generate content hash to avoid duplicates
        content_str = json.dumps(resume_data.model_dump(), sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if resume already exists
            cursor.execute("SELECT id FROM resumes WHERE content_hash = ?", (content_hash,))
            existing = cursor.fetchone()
            
            if existing:
                return existing[0]
            
            # Generate new ID
            resume_id = str(uuid.uuid4())
            
            # Insert new resume
            cursor.execute("""
                INSERT INTO resumes (id, filename, content_hash, data)
                VALUES (?, ?, ?, ?)
            """, (resume_id, filename, content_hash, content_str))
            
            conn.commit()
            return resume_id
    
    def save_job_description(self, job_data: JobPosting) -> str:
        """
        Save job description to database.
        
        Args:
            job_data: Parsed job description data
            
        Returns:
            Job ID
        """
        # Generate content hash to avoid duplicates
        content_str = json.dumps(job_data.model_dump(), sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if job already exists
            cursor.execute("SELECT id FROM job_descriptions WHERE content_hash = ?", (content_hash,))
            existing = cursor.fetchone()
            
            if existing:
                return existing[0]
            
            # Generate new ID if not provided
            job_id = getattr(job_data, 'id', None) or str(uuid.uuid4())
            
            # Insert new job
            cursor.execute("""
                INSERT INTO job_descriptions (id, title, company, content_hash, data)
                VALUES (?, ?, ?, ?, ?)
            """, (job_id, job_data.title, job_data.company, content_hash, content_str))
            
            conn.commit()
            return job_id
    
    def save_match_result(self, match_result: MatchResult) -> str:
        """
        Save match result to database.
        
        Args:
            match_result: Match result data
            
        Returns:
            Match result ID
        """
        match_id = str(uuid.uuid4())
        content_str = json.dumps(match_result.model_dump(), sort_keys=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO match_results (id, resume_id, job_id, overall_score, match_level, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                match_id,
                match_result.resume_id,
                match_result.job_id,
                match_result.overall_match.score,
                match_result.overall_match.match_level.value,
                content_str
            ))
            
            conn.commit()
            return match_id
    
    def get_resume(self, resume_id: str) -> Optional[ResumeData]:
        """Retrieve resume by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM resumes WHERE id = ?", (resume_id,))
            result = cursor.fetchone()
            
            if result:
                data = json.loads(result[0])
                return ResumeData(**data)
            return None
    
    def get_job_description(self, job_id: str) -> Optional[JobPosting]:
        """Retrieve job description by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM job_descriptions WHERE id = ?", (job_id,))
            result = cursor.fetchone()
            
            if result:
                data = json.loads(result[0])
                return JobPosting(**data)
            return None
    
    def get_match_result(self, match_id: str) -> Optional[MatchResult]:
        """Retrieve match result by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM match_results WHERE id = ?", (match_id,))
            result = cursor.fetchone()
            
            if result:
                data = json.loads(result[0])
                return MatchResult(**data)
            return None
    
    def list_resumes(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all resumes with metadata."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, filename, created_at, updated_at
                FROM resumes
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            results: List[Dict[str, Any]] = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'filename': row[1],
                    'created_at': row[2],
                    'updated_at': row[3]
                })
            
            return results
    
    def list_jobs(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all job descriptions with metadata."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, company, created_at, updated_at
                FROM job_descriptions
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            results: List[Dict[str, Any]] = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'title': row[1],
                    'company': row[2],
                    'created_at': row[3],
                    'updated_at': row[4]
                })
            
            return results
    
    def list_matches(self, resume_id: Optional[str] = None, job_id: Optional[str] = None, 
                    limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List match results with optional filtering."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT m.id, m.resume_id, m.job_id, m.overall_score, m.match_level, m.created_at,
                       r.filename as resume_filename, j.title as job_title, j.company
                FROM match_results m
                LEFT JOIN resumes r ON m.resume_id = r.id
                LEFT JOIN job_descriptions j ON m.job_id = j.id
            """
            params: List[Union[str, int]] = []
            
            if resume_id:
                query += " WHERE m.resume_id = ?"
                params.append(resume_id)
            elif job_id:
                query += " WHERE m.job_id = ?"
                params.append(job_id)
            
            query += " ORDER BY m.overall_score DESC, m.created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            results: List[Dict[str, Any]] = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'resume_id': row[1],
                    'job_id': row[2],
                    'overall_score': row[3],
                    'match_level': row[4],
                    'created_at': row[5],
                    'resume_filename': row[6],
                    'job_title': row[7],
                    'company': row[8]
                })
            
            return results
    
    def get_top_matches_for_job(self, job_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top matching resumes for a job."""
        return self.list_matches(job_id=job_id, limit=limit)
    
    def get_matches_for_resume(self, resume_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all matches for a specific resume."""
        return self.list_matches(resume_id=resume_id, limit=limit)
    
    def delete_resume(self, resume_id: str) -> bool:
        """Delete a resume and its associated matches."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete associated matches first
            cursor.execute("DELETE FROM match_results WHERE resume_id = ?", (resume_id,))
            
            # Delete the resume
            cursor.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job description and its associated matches."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete associated matches first
            cursor.execute("DELETE FROM match_results WHERE job_id = ?", (job_id,))
            
            # Delete the job
            cursor.execute("DELETE FROM job_descriptions WHERE id = ?", (job_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM resumes")
            resume_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM job_descriptions")
            job_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM match_results")
            match_count = cursor.fetchone()[0]
            
            # Average match score
            cursor.execute("SELECT AVG(overall_score) FROM match_results")
            avg_score = cursor.fetchone()[0] or 0
            
            # Top matching job
            cursor.execute("""
                SELECT j.title, j.company, AVG(m.overall_score) as avg_score
                FROM match_results m
                JOIN job_descriptions j ON m.job_id = j.id
                GROUP BY j.id
                ORDER BY avg_score DESC
                LIMIT 1
            """)
            top_job = cursor.fetchone()
            
            return {
                'resume_count': resume_count,
                'job_count': job_count,
                'match_count': match_count,
                'average_match_score': round(avg_score, 2),
                'top_matching_job': {
                    'title': top_job[0] if top_job else None,
                    'company': top_job[1] if top_job else None,
                    'average_score': round(top_job[2], 2) if top_job else None
                } if top_job else None
            }
    
    def cleanup_old_matches(self, days: int = 30) -> int:
        """Clean up match results older than specified days."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM match_results 
                WHERE created_at < datetime('now', '-{} days')
            """.format(days))
            
            conn.commit()
            return cursor.rowcount
