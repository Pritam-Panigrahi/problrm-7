from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from models.database import Base
import json

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    phone = Column(String(15), unique=True, nullable=False)
    name = Column(String(100))
    trade = Column(String(100))
    experience_years = Column(Integer)
    location = Column(String(200))
    language = Column(String(10), default='en')
    skills_json = Column(Text)
    education = Column(Text)
    certifications = Column(Text)
    work_history_json = Column(Text)
    chat_history_json = Column(Text)
    resume_complete = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def skills(self):
        if self.skills_json:
            return json.loads(self.skills_json)
        return []
    
    @skills.setter
    def skills(self, value):
        self.skills_json = json.dumps(value)
    
    @property
    def work_history(self):
        if self.work_history_json:
            return json.loads(self.work_history_json)
        return []
    
    @work_history.setter
    def work_history(self, value):
        self.work_history_json = json.dumps(value)
    
    @property
    def chat_history(self):
        if self.chat_history_json:
            return json.loads(self.chat_history_json)
        return []
    
    @chat_history.setter
    def chat_history(self, value):
        self.chat_history_json = json.dumps(value)
