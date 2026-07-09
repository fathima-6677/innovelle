from pydantic import BaseModel
from datetime import datetime

class CommLogCreate(BaseModel):
    wearer_id: str
    category_code: str  # HUNGER, RESTROOM, DISCOMFORT, FEAR, ANXIETY

class CommLogResponse(BaseModel):
    event_id: str
    wearer_id: str
    category_code: str
    timestamp: datetime
