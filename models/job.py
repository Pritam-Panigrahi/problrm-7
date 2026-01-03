from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from datetime import datetime
from models.database import Base
import json

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    title = Column(String(200), nullable=False)
    trade = Column(String(100))
    description = Column(Text)
    required_skills_json = Column(Text)
    experience_required = Column(Integer)
    location = Column(String(200))
    salary_min = Column(Float)
    salary_max = Column(Float)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def required_skills(self):
        if self.required_skills_json:
            return json.loads(self.required_skills_json)
        return []
    
    @required_skills.setter
    def required_skills(self, value):
        self.required_skills_json = json.dumps(value)
