"""
MCP Server implementation for resume analysis
"""

import logging
import json
from typing import Any, Dict, List, Optional
from pathlib import Path

from mcp.server import Server
from mcp.types import Tool, TextContent

try:
    from .config import Config
    from .analyzer import ResumeAnalyzer
    from .models import JobRequirement, EducationLevel
except ImportError:
    from config import Config
    from analyzer import ResumeAnalyzer
    from models import JobRequirement, EducationLevel

class ResumeAnalysisServer:
    """MCP Server for resume analysis operations"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.analyzer = ResumeAnalyzer(config)
          # Validate configuration
        config.validate()
        
    async def register_tools(self, server: Server[Any, Any]):
        """Register all tools with the MCP server"""
        
        @server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="analyze_resume",
                    description="Analyze a single resume file and extract structured data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the resume file (PDF, DOCX, or TXT)"
                            },
                            "job_requirements": {
                                "type": "object",
                                "description": "Optional job requirements for matching",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "required_skills": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "preferred_skills": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "required_experience_years": {"type": "number"},
                                    "required_education": {
                                        "type": "string",
                                        "enum": ["high_school", "associate", "bachelor", "master", "doctorate", "certificate", "other"]
                                    }
                                }
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="batch_analyze_resumes",
                    description="Analyze multiple resume files in batch",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Array of paths to resume files"
                            },
                            "job_requirements": {
                                "type": "object",
                                "description": "Optional job requirements for matching",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "required_skills": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "preferred_skills": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "required_experience_years": {"type": "number"},
                                    "required_education": {"type": "string"}
                                }
                            }
                        },
                        "required": ["file_paths"]
                    }
                ),
                Tool(
                    name="score_resume",
                    description="Score a resume against specific job criteria",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the resume file"
                            },
                            "job_requirements": {
                                "type": "object",
                                "description": "Job requirements for scoring",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "required_skills": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "preferred_skills": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "required_experience_years": {"type": "number"},
                                    "required_education": {"type": "string"}
                                },
                                "required": ["title", "required_skills"]
                            }
                        },
                        "required": ["file_path", "job_requirements"]
                    }
                ),
                Tool(
                    name="sort_resumes",
                    description="Sort and rank multiple analyzed resumes by relevance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Array of paths to resume files"
                            },
                            "job_requirements": {
                                "type": "object",
                                "description": "Optional job requirements for ranking"
                            },
                            "sort_criteria": {
                                "type": "string",
                                "enum": ["overall_score", "experience", "education", "skills"],
                                "description": "Primary sorting criteria"
                            }
                        },
                        "required": ["file_paths"]
                    }
                ),
                Tool(
                    name="filter_resumes",
                    description="Filter resumes based on specific criteria",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_paths": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "filters": {
                                "type": "object",
                                "properties": {
                                    "min_score": {"type": "number", "minimum": 0, "maximum": 1},
                                    "min_experience_years": {"type": "number", "minimum": 0},
                                    "required_skills": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "education_level": {"type": "string"}
                                }
                            }
                        },
                        "required": ["file_paths", "filters"]
                    }
                ),
                Tool(
                    name="extract_skills",
                    description="Extract and categorize skills from resume text",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the resume file"
                            },
                            "skill_categories": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["technical", "soft", "language", "certification", "tool", "framework"]
                                },
                                "description": "Skill categories to extract"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="generate_report",
                    description="Generate a comprehensive analysis report",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_paths": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "job_requirements": {
                                "type": "object",
                                "description": "Optional job requirements for the report"
                            },
                            "report_format": {
                                "type": "string",
                                "enum": ["json", "summary", "detailed"],
                                "description": "Report format type"
                            }
                        },
                        "required": ["file_paths"]
                    }
                ),
                Tool(
                    name="match_job",
                    description="Find best resume matches for a specific job description",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_paths": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "job_description": {
                                "type": "string",
                                "description": "Full job description text"
                            },
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of matches to return",
                                "minimum": 1,
                                "maximum": 50
                            }
                        },
                        "required": ["file_paths", "job_description"]
                    }
                )
            ]
        
        @server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "analyze_resume":
                    return await self._handle_analyze_resume(arguments)
                elif name == "batch_analyze_resumes":
                    return await self._handle_batch_analyze_resumes(arguments)
                elif name == "score_resume":
                    return await self._handle_score_resume(arguments)
                elif name == "sort_resumes":
                    return await self._handle_sort_resumes(arguments)
                elif name == "filter_resumes":
                    return await self._handle_filter_resumes(arguments)
                elif name == "extract_skills":
                    return await self._handle_extract_skills(arguments)
                elif name == "generate_report":
                    return await self._handle_generate_report(arguments)
                elif name == "match_job":
                    return await self._handle_match_job(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
            except Exception as e:
                self.logger.error(f"Tool {name} failed: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _handle_analyze_resume(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle single resume analysis"""
        file_path = args["file_path"]
        job_req = self._parse_job_requirements(args.get("job_requirements"))
        
        # Validate file path
        if not Path(file_path).exists():
            return [TextContent(type="text", text=f"File not found: {file_path}")]
          result = await self.analyzer.analyze_single_resume(file_path, job_req)
        
        response: Dict[str, Any] = {
            "resume_analysis": {
                "file_path": result.resume.file_path,
                "candidate_name": result.resume.contact_info.name,
                "email": result.resume.contact_info.email,
                "phone": result.resume.contact_info.phone,
                "summary": result.resume.summary,
                "total_experience_years": result.resume.total_experience_years,
                "education_count": len(result.resume.education),
                "skills_count": len(result.resume.skills),
                "parsing_confidence": result.resume.parsing_confidence
            },
            "scoring": {
                "overall_score": result.score.overall_score,
                "experience_score": result.score.experience_score,
                "education_score": result.score.education_score,
                "skills_score": result.score.skills_score,
                "achievements_score": result.score.achievements_score,
                "matching_skills": result.score.matching_skills,
                "missing_skills": result.score.missing_skills,
                "recommendation": result.score.recommendation,
                "confidence": result.score.confidence
            },
            "job_match": {
                "match_percentage": result.job_match_percentage,
                "experience_gap": result.score.experience_gap
            },
            "processing_time_seconds": result.processing_time
        }
        
        return [TextContent(type="text", text=json.dumps(response, indent=2))]
      async def _handle_batch_analyze_resumes(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle batch resume analysis"""
        file_paths = args["file_paths"]
        job_req = self._parse_job_requirements(args.get("job_requirements"))
        
        # Validate file paths
        valid_paths: List[str] = []
        invalid_paths: List[str] = []
        
        for path in file_paths:
            if Path(path).exists():
                valid_paths.append(path)
            else:
                invalid_paths.append(path)
        
        if invalid_paths:
            self.logger.warning(f"Invalid file paths: {invalid_paths}")
        
        if not valid_paths:
            return [TextContent(type="text", text="No valid file paths provided")]
        
        results = await self.analyzer.analyze_batch_resumes(valid_paths, job_req)
        sorted_results = self.analyzer.sort_resumes_by_relevance(results, job_req)
        
        response: Dict[str, Any] = {
            "batch_analysis": {
                "total_processed": len(results),
                "total_requested": len(file_paths),
                "invalid_files": invalid_paths,
                "average_score": sum(r.score.overall_score for r in results) / len(results) if results else 0,
                "processing_completed": True
            },
            "results": [
                {
                    "rank": result.ranking,
                    "file_path": result.resume.file_path,
                    "candidate_name": result.resume.contact_info.name,
                    "email": result.resume.contact_info.email,
                    "overall_score": result.score.overall_score,
                    "job_match_percentage": result.job_match_percentage,
                    "experience_years": result.resume.total_experience_years,
                    "skills_count": len(result.resume.skills),
                    "recommendation": result.score.recommendation[:100] + "..." if len(result.score.recommendation) > 100 else result.score.recommendation
                }
                for result in sorted_results
            ]
        }
        
        return [TextContent(type="text", text=json.dumps(response, indent=2))]
      async def _handle_score_resume(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle resume scoring against job requirements"""
        file_path = args["file_path"]
        job_req = self._parse_job_requirements(args["job_requirements"])
        
        if not Path(file_path).exists():
            return [TextContent(type="text", text=f"File not found: {file_path}")]
        
        result = await self.analyzer.analyze_single_resume(file_path, job_req)
        
        response: Dict[str, Any] = {
            "scoring_analysis": {
                "candidate": result.resume.contact_info.name,
                "job_title": job_req.title if job_req else "Not specified",
                "overall_score": result.score.overall_score,
                "score_breakdown": {
                    "experience": result.score.experience_score,
                    "education": result.score.education_score,
                    "skills": result.score.skills_score,
                    "achievements": result.score.achievements_score
                },
                "job_match_percentage": result.job_match_percentage,
                "matching_skills": result.score.matching_skills,
                "missing_skills": result.score.missing_skills,
                "strengths": result.score.strengths,
                "weaknesses": result.score.weaknesses,
                "experience_gap_years": result.score.experience_gap,
                "recommendation": result.score.recommendation,
                "confidence": result.score.confidence
            }
        }
        
        return [TextContent(type="text", text=json.dumps(response, indent=2))]
    
    async def _handle_sort_resumes(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle resume sorting and ranking"""
        file_paths = args["file_paths"]
        job_req = self._parse_job_requirements(args.get("job_requirements"))
        sort_criteria = args.get("sort_criteria", "overall_score")
        
        # Analyze all resumes
        results = await self.analyzer.analyze_batch_resumes(file_paths, job_req)
        
        # Sort based on criteria
        if sort_criteria == "experience":
            results.sort(key=lambda r: r.resume.total_experience_years, reverse=True)
        elif sort_criteria == "education":
            results.sort(key=lambda r: r.score.education_score, reverse=True)
        elif sort_criteria == "skills":
            results.sort(key=lambda r: r.score.skills_score, reverse=True)
        else:  # overall_score
            results = self.analyzer.sort_resumes_by_relevance(results, job_req)
          # Update rankings
        for i, result in enumerate(results, 1):
            result.ranking = i
        
        response: Dict[str, Any] = {
            "sorted_resumes": {
                "sort_criteria": sort_criteria,
                "total_candidates": len(results),
                "job_requirements_applied": job_req is not None,
                "rankings": [
                    {
                        "rank": result.ranking,
                        "candidate_name": result.resume.contact_info.name,
                        "file_path": result.resume.file_path,
                        "overall_score": result.score.overall_score,
                        "job_match_percentage": result.job_match_percentage,
                        "experience_years": result.resume.total_experience_years,
                        "key_strengths": result.score.strengths[:3]
                    }
                    for result in results
                ]
            }
        }
        
        return [TextContent(type="text", text=json.dumps(response, indent=2))]
    
    async def _handle_filter_resumes(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle resume filtering"""
        file_paths = args["file_paths"]
        filters = args["filters"]
        
        # Analyze all resumes first
        results = await self.analyzer.analyze_batch_resumes(file_paths)
        
        # Apply filters
        filtered_results = self.analyzer.filter_resumes_by_criteria(
            results,
            min_score=filters.get("min_score", 0.0),
            min_experience=filters.get("min_experience_years", 0.0),
            required_skills=filters.get("required_skills"),
            education_level=EducationLevel(filters["education_level"]) if filters.get("education_level") else None
        )
          response: Dict[str, Any] = {
            "filtering_results": {
                "original_count": len(results),
                "filtered_count": len(filtered_results),
                "filters_applied": filters,
                "filtered_candidates": [
                    {
                        "candidate_name": result.resume.contact_info.name,
                        "file_path": result.resume.file_path,
                        "overall_score": result.score.overall_score,
                        "experience_years": result.resume.total_experience_years,
                        "education_levels": [edu.level.value for edu in result.resume.education],
                        "skills": [skill.name for skill in result.resume.skills]
                    }
                    for result in filtered_results
                ]
            }
        }
        
        return [TextContent(type="text", text=json.dumps(response, indent=2))]
    
    async def _handle_extract_skills(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle skills extraction"""
        file_path = args["file_path"]
        skill_categories = args.get("skill_categories", ["technical", "soft"])
        
        if not Path(file_path).exists():
            return [TextContent(type="text", text=f"File not found: {file_path}")]
        
        resume = await self.analyzer.parser.parse_file(file_path)
          # Filter skills by requested categories
        filtered_skills: List[Dict[str, Any]] = []
        for skill in resume.skills:
            if skill.category.value in skill_categories:
                filtered_skills.append({
                    "name": skill.name,
                    "category": skill.category.value,
                    "proficiency_level": skill.proficiency_level,
                    "years_experience": skill.years_experience
                })
        
        # Group by category
        skills_by_category: Dict[str, List[Dict[str, Any]]] = {}
        for skill in filtered_skills:
            category = skill["category"]
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill)
          response: Dict[str, Any] = {
            "skills_extraction": {
                "candidate": resume.contact_info.name,
                "file_path": file_path,
                "total_skills_found": len(filtered_skills),
                "categories_requested": skill_categories,
                "skills_by_category": skills_by_category,
                "parsing_confidence": resume.parsing_confidence
            }
        }
        
        return [TextContent(type="text", text=json.dumps(response, indent=2))]
    
    async def _handle_generate_report(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle report generation"""
        file_paths = args["file_paths"]
        job_req = self._parse_job_requirements(args.get("job_requirements"))
        report_format = args.get("report_format", "detailed")
        
        # Analyze all resumes
        results = await self.analyzer.analyze_batch_resumes(file_paths, job_req)
        
        # Generate comprehensive report
        report = await self.analyzer.generate_analysis_report(results, job_req)
        
        if report_format == "summary":
            # Return summarized version
            summary = {
                "report_summary": {
                    "total_candidates": report["analysis_summary"]["total_candidates"],
                    "average_score": report["analysis_summary"]["average_score"],
                    "top_3_candidates": report["top_candidates"][:3],
                    "most_common_skills": report["skills_analysis"]["most_common_skills"][:5]
                }
            }
            return [TextContent(type="text", text=json.dumps(summary, indent=2))]
        else:
            # Return full detailed report
            return [TextContent(type="text", text=json.dumps(report, indent=2))]
    
    async def _handle_match_job(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle job matching"""
        file_paths = args["file_paths"]
        job_description = args["job_description"]
        max_results = args.get("max_results", 10)
        
        # Parse job description to extract requirements
        # This is a simplified implementation - in practice, you'd use NLP to extract requirements
        job_req = JobRequirement(
            title="Extracted from description",
            description=job_description,
            required_skills=self._extract_skills_from_text(job_description),
            required_experience_years=self._extract_experience_from_text(job_description)
        )
        
        # Analyze resumes against job requirements
        results = await self.analyzer.analyze_batch_resumes(file_paths, job_req)
        sorted_results = self.analyzer.sort_resumes_by_relevance(results, job_req)
        
        # Return top matches
        top_matches = sorted_results[:max_results]
          response: Dict[str, Any] = {
            "job_matching": {
                "job_description_summary": job_description[:200] + "..." if len(job_description) > 200 else job_description,
                "extracted_requirements": {
                    "skills": job_req.required_skills,
                    "experience_years": job_req.required_experience_years
                },
                "total_candidates_analyzed": len(results),
                "top_matches": [
                    {
                        "rank": match.ranking,
                        "candidate_name": match.resume.contact_info.name,
                        "email": match.resume.contact_info.email,
                        "job_match_percentage": match.job_match_percentage,
                        "overall_score": match.score.overall_score,
                        "matching_skills": match.score.matching_skills,
                        "experience_years": match.resume.total_experience_years,
                        "strengths": match.score.strengths[:3],
                        "recommendation": match.score.recommendation
                    }
                    for match in top_matches
                ]
            }
        }
        
        return [TextContent(type="text", text=json.dumps(response, indent=2))]
    
    # Public API methods for web integration
    async def analyze_resume_api(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Public wrapper for resume analysis"""
        try:
            result = await self._handle_analyze_resume(args)
            return [{"text": result[0].text}] if result else []
        except Exception as e:
            return [{"error": str(e)}]
    
    async def batch_analyze_resumes_api(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Public wrapper for batch resume analysis"""
        try:
            result = await self._handle_batch_analyze_resumes(args)
            return [{"text": result[0].text}] if result else []
        except Exception as e:
            return [{"error": str(e)}]
    
    async def score_resume_api(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Public wrapper for resume scoring"""
        try:
            result = await self._handle_score_resume(args)
            return [{"text": result[0].text}] if result else []
        except Exception as e:
            return [{"error": str(e)}]
    
    async def sort_resumes_api(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Public wrapper for resume sorting"""
        try:
            result = await self._handle_sort_resumes(args)
            return [{"text": result[0].text}] if result else []
        except Exception as e:
            return [{"error": str(e)}]
    
    async def filter_resumes_api(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Public wrapper for resume filtering"""
        try:
            result = await self._handle_filter_resumes(args)
            return [{"text": result[0].text}] if result else []
        except Exception as e:
            return [{"error": str(e)}]
    
    async def match_job_api(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Public wrapper for job matching"""
        try:
            result = await self._handle_match_job(args)
            return [{"text": result[0].text}] if result else []
        except Exception as e:
            return [{"error": str(e)}]
    
    async def extract_skills_api(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Public wrapper for skills extraction"""
        try:
            result = await self._handle_extract_skills(args)
            return [{"text": result[0].text}] if result else []
        except Exception as e:
            return [{"error": str(e)}]
    
    async def generate_report_api(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Public wrapper for report generation"""
        try:
            result = await self._handle_generate_report(args)
            return [{"text": result[0].text}] if result else []
        except Exception as e:
            return [{"error": str(e)}]
    
    def _parse_job_requirements(self, job_req_dict: Optional[Dict[str, Any]]) -> Optional[JobRequirement]:
        """Parse job requirements from dictionary"""
        if not job_req_dict:
            return None
        
        education_level = EducationLevel.OTHER
        if "required_education" in job_req_dict:
            try:
                education_level = EducationLevel(job_req_dict["required_education"])
            except ValueError:
                pass
        
        return JobRequirement(
            title=job_req_dict.get("title", ""),
            description=job_req_dict.get("description", ""),
            required_skills=job_req_dict.get("required_skills", []),
            preferred_skills=job_req_dict.get("preferred_skills", []),
            required_experience_years=job_req_dict.get("required_experience_years", 0),
            required_education=education_level,
            location=job_req_dict.get("location", ""),
            salary_range=job_req_dict.get("salary_range", "")
        )
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description text"""
        # Simplified skill extraction - in practice, use NLP
        common_skills = [
            "python", "java", "javascript", "react", "angular", "vue",
            "node.js", "express", "django", "flask", "sql", "aws", "docker"        ]
        
        text_lower = text.lower()
        found_skills: List[str] = []
        
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_experience_from_text(self, text: str) -> int:
        """Extract experience requirements from job description"""
        import re
        
        # Look for patterns like "3+ years", "5 years experience", etc.
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*years?\s*(?:in|with)',
            r'minimum\s*(?:of\s*)?(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return 0  # Default to 0 if no experience requirement found
