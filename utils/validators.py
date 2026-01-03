import re
import bleach

def validate_indian_phone(phone):
    pattern = r'^[6-9]\d{9}$'
    cleaned = re.sub(r'[^\d]', '', phone)
    return bool(re.match(pattern, cleaned))

def sanitize_input(text):
    if not text:
        return ""
    return bleach.clean(str(text), tags=[], strip=True)

def validate_required_fields(data, required_fields):
    missing = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing.append(field)
    return missing
