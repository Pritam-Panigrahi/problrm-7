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

def extract_and_categorize_skills(skills_list, trade):
    prompt = f"""You are a skills categorization expert for blue-collar trades.
    
Trade: {trade}
Raw skills: {', '.join(skills_list)}

Normalize, expand, and categorize these skills into:
1. Technical Skills - trade-specific abilities
2. Soft Skills - communication, teamwork, problem-solving
3. Tools & Equipment - specific tools they can use

Return JSON:
{{
    "technical_skills": ["..."],
    "soft_skills": ["..."],
    "tools_equipment": ["..."]
}}

Make skills professional and ATS-friendly."""
    
    try:
        response = get_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            return json.loads(response.text)
        return {
            "technical_skills": skills_list,
            "soft_skills": [],
            "tools_equipment": []
        }
    
    except Exception as e:
        print(f"Error categorizing skills: {e}")
        return {
            "technical_skills": skills_list,
            "soft_skills": [],
            "tools_equipment": []
        }
