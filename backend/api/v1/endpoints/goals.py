from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Goal, ProgressUpdate
from services.ai import AIService
from datetime import datetime
from typing import Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/create")
async def create_goal(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        data = await request.json()
        
        goal = Goal(
            user_id=int(user_id),
            category=data['category'],
            description=data['description'],
            target_date=datetime.strptime(data['target_date'], '%Y-%m-%d').date()
        )
    
        db.add(goal)
        await db.commit()
        await db.refresh(goal)
    
        return {
            "success": True,
            "goal": {
                "id": goal.id,
                "category": goal.category,
                "description": goal.description,
                "target_date": goal.target_date.isoformat(),
                "created_at": goal.created_at.isoformat()
            }
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating goal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_goals(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        # Get user_id from session and convert to int
        session_user_id = request.session.get('user_id')
        if not session_user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        try:
            session_user_id = int(session_user_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid session")

        # Verify user authorization
        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Fetch goals
        query = select(Goal).filter(Goal.user_id == user_id)
        result = await db.execute(query)
        goals = result.scalars().all()

        # Format goals according to expected response format
        formatted_goals = []
        for goal in goals:
            # Get latest progress
            progress_query = select(ProgressUpdate).filter(
                ProgressUpdate.goal_id == goal.id
            ).order_by(ProgressUpdate.created_at.desc())
            progress_result = await db.execute(progress_query)
            latest_progress = progress_result.scalar_one_or_none()

            formatted_goals.append({
                "id": goal.id,
                "category": goal.category,
                "description": goal.description,
                "target_date": goal.target_date.isoformat(),
                "created_at": goal.created_at.isoformat(),
                "progress": latest_progress.progress_value if latest_progress else 0
            })

        return {
            "success": True,
            "goals": formatted_goals
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching goals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions/{user_id}")
async def get_suggestions(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    logger.info(f"Getting suggestions for user_id: {user_id}")
    try:
        if not request.session.get('user_id'):
            logger.warning("User not authenticated")
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "detail": "Not authenticated"
                }
            )
        
        # Get user's goals for context
        query = select(Goal).filter(Goal.user_id == user_id)
        result = await db.execute(query)
        goals = result.scalars().all()
        
        # If no goals yet, return starter suggestions
        if not goals:
            logger.info("No goals found, returning starter suggestions")
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "suggestions": [
                        "Start by creating a SMART goal - Specific, Measurable, Achievable, Relevant, and Time-bound",
                        "Consider breaking down your future goals into smaller, manageable tasks",
                        "Set up regular check-ins to track your progress"
                    ]
                }
            )

        # If there are goals, create suggestions based on them
        suggestions = [
            f"For your {goals[0].category} goal: Break down '{goals[0].description}' into weekly milestones",
            "Schedule weekly review sessions to track your progress",
            "Consider setting reminders for your daily tasks"
        ]

        logger.info(f"Successfully generated suggestions for user_id: {user_id}")
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "suggestions": suggestions
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "detail": "Error getting suggestions"
            }
        )

@router.put("/update")
async def update_goal(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        data = await request.json()
        goal = await db.get(Goal, data['id'])
        
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        if str(goal.user_id) != str(user_id):
            raise HTTPException(status_code=403, detail="Not authorized")

        if 'category' in data:
            goal.category = data['category']
        if 'description' in data:
            goal.description = data['description']
        if 'target_date' in data:
            goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()

        await db.commit()
        await db.refresh(goal)
        
        return {
            "success": True,
            "goal": {
                "id": goal.id,
                "category": goal.category,
                "description": goal.description,
                "target_date": goal.target_date.isoformat(),
                "created_at": goal.created_at.isoformat()
            }
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating goal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        goal = await db.get(Goal, goal_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        if str(goal.user_id) != str(user_id):
            raise HTTPException(status_code=403, detail="Not authorized")

        await db.delete(goal)
        await db.commit()
        
        return {
            "success": True,
            "message": "Goal deleted successfully"
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting goal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
