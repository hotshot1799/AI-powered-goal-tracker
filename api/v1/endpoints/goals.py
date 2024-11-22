from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from app.services.goals import GoalService
from app.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> GoalResponse:
    goal_service = GoalService(db)
    return await goal_service.create_goal(current_user.id, goal_data)

@router.get("", response_model=List[GoalResponse])
async def get_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[GoalResponse]:
    goal_service = GoalService(db)
    return await goal_service.get_user_goals(current_user.id)
