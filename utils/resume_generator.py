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

def generate_ats_resume_content(user_data):
    prompt = f"""Generate a professional, ATS-friendly, one-page resume for a blue-collar worker.

Worker Data:
{json.dumps(user_data, indent=2)}

Requirements:
1. Professional SUMMARY (3-4 lines with quantifiable achievements)
2. EXPERIENCE section (action verbs, quantified results)
3. SKILLS section (categorized: Technical, Tools/Equipment, Soft Skills)
4. CERTIFICATIONS (if any)
5. EDUCATION (if any)

Use trade-specific keywords and phrases.
Format for easy parsing by ATS systems.
One page maximum.

Return plain text resume."""
    
    try:
        response = get_client().models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3
            )
        )
        
        return response.text if response.text else "Resume generation failed"
    
    except Exception as e:
        print(f"Error generating resume: {e}")
        return "Resume generation failed"
