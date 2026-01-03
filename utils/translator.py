import os
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

def translate_text(text, target_language='hi'):
    if target_language == 'en':
        return text
    
    language_map = {
        'hi': 'Hindi',
        'en': 'English',
        'or': 'Odia'
    }
    
    target_lang_name = language_map.get(target_language, 'Hindi')
    
    prompt = f"Translate the following text to {target_lang_name}. Return only the translation:\n\n{text}"
    
    try:
        response = get_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        return response.text if response.text else text
    
    except Exception as e:
        print(f"Translation error: {e}")
        return text
