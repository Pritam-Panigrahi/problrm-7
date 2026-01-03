import os
import json
from google import genai
from google.genai import types
from config import Config

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or getattr(Config, "GEMINI_API_KEY", None)
        )
        if api_key:
            api_key = api_key.strip().strip('"').strip("'")
        if not api_key:
            raise ValueError("Gemini API key not configured. Set GEMINI_API_KEY (or GOOGLE_API_KEY) in your environment.")
        _client = genai.Client(api_key=api_key)
    return _client

def match_jobs_for_user(user_data, jobs_list):
    user_info = f"""
Worker Profile:
- Trade: {user_data.get('trade', 'N/A')}
- Experience: {user_data.get('experience_years', 0)} years
- Skills: {', '.join(user_data.get('skills', []))}
- Location: {user_data.get('location', 'N/A')}
"""
    
    jobs_info = []
    for job in jobs_list:
        jobs_info.append({
            "job_id": job.get('id'),
            "title": job.get('title'),
            "trade": job.get('trade'),
            "required_skills": job.get('required_skills', []),
            "experience_required": job.get('experience_required', 0),
            "location": job.get('location'),
            "salary_range": f"{job.get('salary_min', 0)}-{job.get('salary_max', 0)}"
        })
    
    prompt = f"""{user_info}

Available Jobs:
{json.dumps(jobs_info, indent=2)}

Score each job for this worker on a scale of 1-10 based on:
- Skill overlap (40%)
- Experience match (30%)
- Location proximity (20%)
- Growth potential (10%)

Return JSON array sorted by score (highest first):
[
    {{
        "job_id": 1,
        "score": 8.5,
        "reasoning": "Strong skill match, location nearby, slightly more experience than required"
    }}
]

Return only top 10 matches."""
    
    try:
        response = get_client().models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            return json.loads(response.text)
        return []
    
    except Exception as e:
        print(f"Error matching jobs: {e}")
        return []
