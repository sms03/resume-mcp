"""
Claude response formatter for resume analysis results
"""
from typing import Dict, Any, List, Optional

class ClaudeResponseFormatter:
    """Format resume analysis results for Claude responses"""
    
    @staticmethod
    def format_resume_analysis(analysis: Dict[str, Any]) -> str:
        """
        Format resume analysis results for Claude
        
        Args:
            analysis: The analysis results from the resume analyzer
            
        Returns:
            str: Formatted text response for Claude
        """
        if not analysis or "error" in analysis:
            return f"Error analyzing resume: {analysis.get('error', 'Unknown error')}"
        
        # Extract the main sections
        personal_info = analysis.get("personal_info", {})
        summary = analysis.get("summary", "No summary available")
        skills = analysis.get("skills", [])
        education = analysis.get("education", [])
        experience = analysis.get("experience", [])
        projects = analysis.get("projects", [])
        certifications = analysis.get("certifications", [])
        
        # Format the response
        response = "# Resume Analysis\n\n"
        
        # Personal Information
        response += "## Personal Information\n"
        if personal_info:
            for key, value in personal_info.items():
                if value:
                    response += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        else:
            response += "No personal information found\n"
        
        # Summary
        response += "\n## Summary\n"
        response += f"{summary}\n"
        
        # Skills
        response += "\n## Skills\n"
        if skills:
            response += ", ".join(skills) + "\n"
        else:
            response += "No skills found\n"
        
        # Education
        response += "\n## Education\n"
        if education:
            for edu in education:
                institution = edu.get("institution", "Unknown Institution")
                degree = edu.get("degree", "")
                field = edu.get("field", "")
                dates = edu.get("dates", "")
                gpa = edu.get("gpa", "")
                
                response += f"### {institution}\n"
                if degree or field:
                    response += f"- **Degree**: {degree} {field}\n"
                if dates:
                    response += f"- **Dates**: {dates}\n"
                if gpa:
                    response += f"- **GPA**: {gpa}\n"
                response += "\n"
        else:
            response += "No education history found\n"
        
        # Experience
        response += "\n## Professional Experience\n"
        if experience:
            for exp in experience:
                company = exp.get("company", "Unknown Company")
                title = exp.get("title", "")
                dates = exp.get("dates", "")
                description = exp.get("description", "")
                achievements = exp.get("achievements", [])
                
                response += f"### {title} at {company}\n"
                if dates:
                    response += f"**{dates}**\n\n"
                if description:
                    response += f"{description}\n\n"
                
                if achievements:
                    response += "**Key Achievements:**\n"
                    for achievement in achievements:
                        response += f"- {achievement}\n"
                response += "\n"
        else:
            response += "No professional experience found\n"
        
        # Projects
        response += "\n## Projects\n"
        if projects:
            for project in projects:
                name = project.get("name", "Unnamed Project")
                description = project.get("description", "")
                technologies = project.get("technologies", [])
                url = project.get("url", "")
                
                response += f"### {name}\n"
                if description:
                    response += f"{description}\n\n"
                
                if technologies:
                    response += f"**Technologies**: {', '.join(technologies)}\n"
                
                if url:
                    response += f"**URL**: {url}\n"
                
                response += "\n"
        else:
            response += "No projects found\n"
        
        # Certifications
        response += "\n## Certifications\n"
        if certifications:
            for cert in certifications:
                name = cert.get("name", "")
                issuer = cert.get("issuer", "")
                date = cert.get("date", "")
                
                response += f"- **{name}** - {issuer}"
                if date:
                    response += f" ({date})"
                response += "\n"
        else:
            response += "No certifications found\n"
        
        return response
    
    @staticmethod
    def format_resume_job_match(match_results: Dict[str, Any]) -> str:
        """
        Format resume-job match results for Claude
        
        Args:
            match_results: The match results from the resume analyzer
            
        Returns:
            str: Formatted text response for Claude
        """
        if not match_results or "error" in match_results:
            return f"Error matching resume to job: {match_results.get('error', 'Unknown error')}"
        
        # Extract the main sections
        match_score = match_results.get("match_score", 0)
        skill_match = match_results.get("skill_match", {})
        experience_match = match_results.get("experience_match", {})
        education_match = match_results.get("education_match", {})
        highlights = match_results.get("highlights", [])
        concerns = match_results.get("concerns", [])
        recommendations = match_results.get("recommendations", "")
        
        # Format the response
        response = "# Resume-Job Match Analysis\n\n"
        
        # Overall score with progress bar visualization
        progress_bar_length = 20
        filled_length = int(round(progress_bar_length * match_score / 100))
        progress_bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
        
        response += "## Overall Match Score\n"
        response += f"**{match_score}/100** {progress_bar}\n\n"
        
        # Skill match
        response += "## Skill Match\n"
        if skill_match:
            skill_score = skill_match.get("score", 0)
            filled_length = int(round(progress_bar_length * skill_score / 100))
            progress_bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
            response += f"**Score**: {skill_score}/100 {progress_bar}\n\n"
            
            matched_skills = skill_match.get("matched_skills", [])
            missing_skills = skill_match.get("missing_skills", [])
            explanation = skill_match.get("explanation", "")
            
            if matched_skills:
                response += "**Matched Skills**:\n"
                for skill in matched_skills:
                    response += f"- {skill}\n"
                response += "\n"
            
            if missing_skills:
                response += "**Missing Skills**:\n"
                for skill in missing_skills:
                    response += f"- {skill}\n"
                response += "\n"
            
            if explanation:
                response += f"**Analysis**: {explanation}\n\n"
        else:
            response += "No skill match information available\n\n"
        
        # Experience match
        response += "## Experience Match\n"
        if experience_match:
            exp_score = experience_match.get("score", 0)
            filled_length = int(round(progress_bar_length * exp_score / 100))
            progress_bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
            response += f"**Score**: {exp_score}/100 {progress_bar}\n\n"
            
            explanation = experience_match.get("explanation", "")
            if explanation:
                response += f"**Analysis**: {explanation}\n\n"
        else:
            response += "No experience match information available\n\n"
        
        # Education match
        response += "## Education Match\n"
        if education_match:
            edu_score = education_match.get("score", 0)
            filled_length = int(round(progress_bar_length * edu_score / 100))
            progress_bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
            response += f"**Score**: {edu_score}/100 {progress_bar}\n\n"
            
            explanation = education_match.get("explanation", "")
            if explanation:
                response += f"**Analysis**: {explanation}\n\n"
        else:
            response += "No education match information available\n\n"
        
        # Highlights
        response += "## Key Strengths\n"
        if highlights:
            for highlight in highlights:
                response += f"- {highlight}\n"
            response += "\n"
        else:
            response += "No key strengths identified\n\n"
        
        # Concerns
        response += "## Areas of Concern\n"
        if concerns:
            for concern in concerns:
                response += f"- {concern}\n"
            response += "\n"
        else:
            response += "No concerns identified\n\n"
        
        # Recommendations
        response += "## Recommendations\n"
        if recommendations:
            response += f"{recommendations}\n"
        else:
            response += "No specific recommendations\n"
        
        return response
    
    @staticmethod
    def format_candidate_rankings(rankings: List[Dict[str, Any]]) -> str:
        """
        Format candidate ranking results for Claude
        
        Args:
            rankings: The ranking results from the resume analyzer
            
        Returns:
            str: Formatted text response for Claude
        """
        if not rankings:
            return "No candidates to rank"
        
        if isinstance(rankings, dict) and "error" in rankings:
            return f"Error ranking candidates: {rankings.get('error', 'Unknown error')}"
        
        # Format the response
        response = "# Candidate Rankings\n\n"
        
        # Create a table header
        response += "| Rank | ID | Match Score | Recommendation |\n"
        response += "|------|----|-----------:|----------------|\n"
        
        # Add each candidate to the table
        for i, candidate in enumerate(rankings):
            rank = i + 1
            candidate_id = candidate.get("id", f"Candidate {rank}")
            match_score = candidate.get("match_score", 0)
            recommendation = candidate.get("recommendation", "No recommendation")
            
            response += f"| {rank} | {candidate_id} | {match_score}/100 | {recommendation} |\n"
        
        # Add detailed candidate information
        response += "\n## Detailed Candidate Information\n\n"
        
        for i, candidate in enumerate(rankings):
            rank = i + 1
            candidate_id = candidate.get("id", f"Candidate {rank}")
            match_score = candidate.get("match_score", 0)
            strengths = candidate.get("strengths", [])
            weaknesses = candidate.get("weaknesses", [])
            recommendation = candidate.get("recommendation", "No recommendation")
            
            response += f"### {rank}. {candidate_id} (Score: {match_score}/100)\n\n"
            
            # Strengths
            response += "**Key Strengths**:\n"
            if strengths:
                for strength in strengths:
                    response += f"- {strength}\n"
            else:
                response += "- No specific strengths identified\n"
            
            # Weaknesses
            response += "\n**Areas for Improvement**:\n"
            if weaknesses:
                for weakness in weaknesses:
                    response += f"- {weakness}\n"
            else:
                response += "- No specific areas for improvement identified\n"
            
            # Recommendation
            response += f"\n**Recommendation**: {recommendation}\n\n"
            
            # Separator between candidates
            response += "---\n\n"
        
        return response
