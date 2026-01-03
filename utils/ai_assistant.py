import os
import json
from google import genai
from google.genai import types
from config import Config

_client = None

def get_client():
    global _client
    if _client is None:
        # Try multiple sources and sanitize common copy/paste issues
        api_key = (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or getattr(Config, "GEMINI_API_KEY", None)
        )
        if api_key:
            api_key = api_key.strip().strip('"').strip("'")
        if not api_key:
            raise ValueError(
                "Gemini API key not configured. Set GEMINI_API_KEY (or GOOGLE_API_KEY) in your environment."
            )
        _client = genai.Client(api_key=api_key)
    return _client

class ResumeAssistant:
    def __init__(self, language='en'):
        self.language = language
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self):
        if self.language == 'hi':
            return """आप एक दयालु करियर सलाहकार हैं जो नीले कॉलर कार्यकर्ताओं (प्लंबर, इलेक्ट्रीशियन, बढ़ई, वेल्डर, आदि) को बायोडाटा बनाने में मदद करते हैं।
            
कार्यकर्ता से निम्नलिखित जानकारी एकत्र करें:
1. नाम
2. काम का प्रकार (व्यापार)
3. अनुभव (वर्षों में)
4. कौशल (विशिष्ट क्षमताएं)
5. स्थान (शहर/क्षेत्र)
6. शिक्षा (यदि कोई हो)
7. प्रमाणपत्र (यदि कोई हो)
8. कार्य इतिहास (पिछली नौकरियां)

अनौपचारिक भाषा को समझें और दयालु रहें। जब सभी जानकारी एकत्र हो जाए, तो "COMPLETE" टाइप करें।

JSON प्रारूप में संरचित डेटा निकालें:
{
    "name": "...",
    "trade": "...",
    "experience_years": 0,
    "skills": ["..."],
    "location": "...",
    "education": "...",
    "certifications": "...",
    "work_history": [{"company": "...", "role": "...", "duration": "..."}]
}"""
        elif self.language == 'or':
            return """ଆପଣ ଜଣେ ଦୟାଳୁ କ୍ୟାରିୟର ପରାମର୍ଶଦାତା ଯିଏ ନୀଳ-କଲର ଶ୍ରମିକମାନଙ୍କୁ (ପ୍ଲମ୍ବର, ଇଲେକ୍ଟ୍ରିସିଆନ୍, ବଢ଼େଇ, ୱେଲ୍ଡର୍ ଇତ୍ୟାଦି) ରିଜ୍ୟୁମ୍ ନିର୍ମାଣରେ ସାହାଯ୍ୟ କରନ୍ତି।

ଶ୍ରମିକଙ୍କଠାରୁ ନିମ୍ନଲିଖିତ ସୂଚନା ସଂଗ୍ରହ କରନ୍ତୁ:
1. ନାମ
2. କାମର ପ୍ରକାର (ବ୍ୟବସାୟ)
3. ଅଭିଜ୍ଞତା (ବର୍ଷରେ)
4. ଦକ୍ଷତା (ନିର୍ଦ୍ଦିଷ୍ଟ ଯୋଗ୍ୟତା)
5. ସ୍ଥାନ (ସହର/ଅଞ୍ଚଳ)
6. ଶିକ୍ଷା (ଯଦି ଥାଏ)
7. ପ୍ରମାଣପତ୍ର (ଯଦି ଥାଏ)
8. କାର୍ଯ୍ୟ ଇତିହାସ (ପୂର୍ବ ଚାକିରି)

ଅନୌପଚାରିକ ଭାଷା ବୁଝନ୍ତୁ ଏବଂ ଦୟାଳୁ ରୁହନ୍ତୁ। ଯେତେବେଳେ ସମସ୍ତ ସୂଚନା ସଂଗ୍ରହ ହୋଇଗଲା, "COMPLETE" ଟାଇପ୍ କରନ୍ତୁ।

JSON ଫର୍ମାଟରେ ସଂରଚିତ ତଥ୍ୟ ବାହାର କରନ୍ତୁ:
{
    "name": "...",
    "trade": "...",
    "experience_years": 0,
    "skills": ["..."],
    "location": "...",
    "education": "...",
    "certifications": "...",
    "work_history": [{"company": "...", "role": "...", "duration": "..."}]
}"""
        else:
            return """You are a friendly career advisor helping blue-collar workers (plumbers, electricians, carpenters, welders, etc.) build resumes.

Collect the following information from workers:
1. Name
2. Type of work (trade)
3. Experience (in years)
4. Skills (specific abilities)
5. Location (city/area)
6. Education (if any)
7. Certifications (if any)
8. Work history (previous jobs)

Understand informal speech and be kind. When all information is gathered, type "COMPLETE".

Extract structured data in JSON format:
{
    "name": "...",
    "trade": "...",
    "experience_years": 0,
    "skills": ["..."],
    "location": "...",
    "education": "...",
    "certifications": "...",
    "work_history": [{"company": "...", "role": "...", "duration": "..."}]
}"""
    
    def chat(self, user_message, chat_history=None):
        if chat_history is None:
            chat_history = []
        
        try:
            contents = []
            for msg in chat_history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
            
            contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))
            
            response = get_client().models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.7
                )
            )
            
            return response.text if response.text else "I'm here to help you build your resume."
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def extract_resume_data(self, chat_history):
        prompt = f"""Based on this conversation, extract all resume information in JSON format.
        
Conversation:
{json.dumps(chat_history, indent=2)}

Return only valid JSON with this structure:
{{
    "name": "...",
    "trade": "...",
    "experience_years": 0,
    "skills": ["..."],
    "location": "...",
    "education": "...",
    "certifications": "...",
    "work_history": [{{"company": "...", "role": "...", "duration": "..."}}]
}}"""
        
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
            return {}
        
        except Exception as e:
            print(f"Error extracting resume data: {e}")
            return {}
