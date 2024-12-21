from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

class GoalBase(BaseModel):
    category: str
    description: str
    target_date: date

class GoalCreate(GoalBase):
    pass

class GoalUpdate(GoalBase):
    pass

class GoalResponse(GoalBase):
    id: int
    user_id: int
    created_at: datetime
    progress: Optional[float] = 0

    class Config:
        from_attributes = True
