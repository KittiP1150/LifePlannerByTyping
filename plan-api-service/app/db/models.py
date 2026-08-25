from sqlalchemy import Column, Integer, String
from app.db.database import Base

class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    date = Column(String(10), index=True)
    start_time = Column(String(10), nullable=True)
    end_time = Column(String(10), nullable=True)
    category = Column(String(50), default="Work")
    priority = Column(String(50), default="Medium")
    
class LocationDB(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), index=True)
    city = Column(String(100), default="Bangkok")