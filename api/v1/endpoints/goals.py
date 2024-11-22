from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from services.goals import GoalService
from database import get_db
from api.v1.deps import get_current_user
from models.user import User

router = APIRouter()

@router.post("", response_model=Dict[str, Any])
async def create_goal(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    if "user_id" not in request.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        data = await request.json()
        data["user_id"] = request.session["user_id"]
        
        goal_service = GoalService(db)
        return await goal_service.create_goal(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/user/{user_id}", response_model=Dict[str, Any])
async def get_goals(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    if "user_id" not in request.session or str(request.session["user_id"]) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )
    
    try:
        goal_service = GoalService(db)
        return await goal_service.get_user_goals(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{goal_id}")
async def update_goal(
    goal_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    if "user_id" not in request.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        data = await request.json()
        goal_service = GoalService(db)
        return await goal_service.update_goal(goal_id, data, request.session["user_id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    if "user_id" not in request.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        goal_service = GoalService(db)
        return await goal_service.delete_goal(goal_id, request.session["user_id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
