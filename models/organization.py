from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from models.database import Base

class Organization(Base):
    __tablename__ = 'organizations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    email = Column(String(100))
    location = Column(String(200))
    industry = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
