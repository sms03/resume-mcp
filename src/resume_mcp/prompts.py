"""
Prompt templates for resume analysis
"""

RESUME_ANALYSIS_PROMPT = """
I need you to analyze the following resume and extract key information in a structured format.
Focus on:
1. Personal information (name, contact, etc.)
2. Education history
3. Work experience
4. Skills (technical and soft)
5. Projects
6. Certifications
7. Summary/highlights

RESUME TEXT:
{resume_text}

Provide your analysis in valid JSON format with the following structure:
{
  "personal_info": {
    "name": "...",
    "email": "...",
    "phone": "...",
    "location": "...",
    "linkedin": "..."
  },
  "summary": "...",
  "skills": ["skill1", "skill2", ...],
  "education": [
    {
      "institution": "...",
      "degree": "...",
      "field": "...",
      "dates": "...",
      "gpa": "..."
    }
  ],
  "experience": [
    {
      "company": "...",
      "title": "...",
      "dates": "...",
      "description": "...",
      "achievements": ["..."]
    }
  ],
  "projects": [
    {
      "name": "...",
      "description": "...",
      "technologies": ["..."],
      "url": "..."
    }
  ],
  "certifications": [
    {
      "name": "...",
      "issuer": "...",
      "date": "..."
    }
  ]
}

IMPORTANT: Provide only valid JSON as your response, with no additional text.
"""

RESUME_JOB_MATCHING_PROMPT = """
I need you to compare a resume against a job description and determine how well the candidate matches the position.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Analyze the match based on:
1. Skills match (required and preferred skills)
2. Experience relevance (years and quality)
3. Education fit
4. Overall suitability

Provide your analysis in valid JSON format with the following structure:
{
  "match_score": 85,  # Overall match score out of 100
  "skill_match": {
    "score": 80,  # Out of 100
    "matched_skills": ["skill1", "skill2", ...],
    "missing_skills": ["skill3", "skill4", ...],
    "explanation": "..."
  },
  "experience_match": {
    "score": 90,  # Out of 100
    "explanation": "..."
  },
  "education_match": {
    "score": 85,  # Out of 100
    "explanation": "..."
  },
  "highlights": [
    "Key strength 1 relevant to the position",
    "Key strength 2 relevant to the position"
  ],
  "concerns": [
    "Potential issue or gap 1",
    "Potential issue or gap 2"
  ],
  "recommendations": "Actions the candidate could take to improve their fit"
}

IMPORTANT: Provide only valid JSON as your response, with no additional text.
"""

CANDIDATE_RANKING_PROMPT = """
I need you to rank multiple candidates based on their resumes against a job description.

JOB DESCRIPTION:
{job_description}

CANDIDATES (in JSON format):
{resumes_json}

Analyze each candidate's match to the job based on:
1. Skills match
2. Experience relevance
3. Education fit
4. Overall suitability

Then rank the candidates from best to worst fit.

Provide your analysis in valid JSON format with the following structure:
{
  "rankings": [
    {
      "id": "candidate_id",
      "match_score": 85,
      "strengths": ["strength1", "strength2"],
      "weaknesses": ["weakness1", "weakness2"],
      "recommendation": "Brief hiring recommendation"
    },
    {
      "id": "candidate_id",
      "match_score": 75,
      ...
    }
  ]
}

IMPORTANT: Provide only valid JSON as your response, with no additional text.
"""
