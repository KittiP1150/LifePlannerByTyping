from pydantic import BaseModel, Field
from typing import List, Optional

class DailyTask(BaseModel):
    title: str = Field(..., description="work title")
    date: str
    start_time: Optional[str] = Field(None, description="start time HH:MM")
    end_time: Optional[str] = Field(None, description="end time HH:MM")
    category: str = Field(..., description="Work, Health, Personal, or Errand")
    priority: str = Field(..., description="High, Medium, or Low")
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    user_message: str
    target_date: str
    
class DailyLocation(BaseModel):
    date: str
    city: str
    
class PlannerResponse(BaseModel):
    reply_message: str
    tasks: List[DailyTask]
    locations: List[DailyLocation]
    