import os
from dotenv import load_dotenv

load_dotenv()

def _clean_env_value(v):
    if not v:
        return None
    return v.strip().strip('"').strip("'")

class Config:
    SECRET_KEY = _clean_env_value(os.environ.get('SECRET_KEY') or os.environ.get('SESSION_SECRET'))
    if not SECRET_KEY:
        import secrets
        SECRET_KEY = secrets.token_hex(32)
    GEMINI_API_KEY = _clean_env_value(os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY'))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///skilllink.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
