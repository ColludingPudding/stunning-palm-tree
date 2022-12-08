from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Submission(Base):
    __tablename__ = "submission"
    hash = Column(String, primary_key=True, index=True)
    author = Column(String)
    full_link = Column(String)
    score = Column(Integer)
    thumbnail = Column(String)	
    thumbnail_height = Column(Integer)
    thumbnail_width = Column(Integer)
    title = Column(String)	
    url = Column(String)	
    
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
