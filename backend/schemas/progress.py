from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProgressUpdateBase(BaseModel):
    update_text: str
    progress_value: Optional[float] = 0

class ProgressUpdateCreate(ProgressUpdateBase):
    goal_id: int

class ProgressUpdateResponse(ProgressUpdateBase):
    id: int
    created_at: datetime
    analysis: Optional[str] = None

    class Config:
        from_attributes = True
