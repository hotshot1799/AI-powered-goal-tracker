from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Goal, ProgressUpdate, User
from services.ai import AIService
from datetime import datetime
from typing import Dict, Any
import logging
from core.security import decode_token

router = APIRouter()
logger = logging.getLogger(__name__)

async def get_user_from_token(request: Request, db: AsyncSession = Depends(get_db)):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            payload = decode_token(token)
            username = payload.get("sub")
            if username:
                query = select(User).filter(User.username == username)
                result = await db.execute(query)
                user = result.scalar_one_or_none()
                if user:
                    return user
        except:
            pass
    
    # Fallback to session if token auth fails
    user_id = request.session.get('user_id')
    if user_id:
        query = select(User).filter(User.id == int(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user:
            return user
    
    raise HTTPException(status_code=401, detail="Not authenticated")

@router.post("/create")
async def create_goal(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_user_from_token)
) -> JSONResponse:
    try:
        data = await request.json()
        
        goal = Goal(
            user_id=current_user.id,
            category=data['category'],
            description=data['description'],
            target_date=datetime.strptime(data['target_date'], '%Y-%m-%d').date()
        )
    
        db.add(goal)
        await db.commit()
        await db.refresh(goal)
    
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "goal": {
                    "id": goal.id,
                    "category": goal.category,
                    "description": goal.description,
                    "target_date": goal.target_date.isoformat(),
                    "created_at": goal.created_at.isoformat()
                }
            }
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating goal: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": str(e)}
        )

@router.get("/user/{user_id}")
async def get_user_goals(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_user_from_token)
) -> JSONResponse:
    try:
        if user_id != current_user.id:
            return JSONResponse(
                status_code=403,
                content={"success": False, "detail": "Not authorized"}
            )

        # Fetch goals
        query = select(Goal).filter(Goal.user_id == user_id)
        result = await db.execute(query)
        goals = result.scalars().all()

        # Format goals
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

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "goals": formatted_goals
            }
        )

    except Exception as e:
        logger.error(f"Error fetching goals: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": str(e)}
        )

@router.get("/suggestions/{user_id}")
async def get_suggestions(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_user_from_token)
) -> JSONResponse:
    logger.info(f"Getting personalized suggestions for user_id: {user_id}")
    try:
        if user_id != current_user.id:
            return JSONResponse(
                status_code=403,
                content={"success": False, "detail": "Not authorized"}
            )
        
        # Get user's goals with progress information
        goals_query = select(Goal).filter(Goal.user_id == user_id)
        result = await db.execute(goals_query)
        goals = result.scalars().all()
        
        # Format goals with their latest progress
        formatted_goals = []
        for goal in goals:
            try:
                # Get latest progress update
                progress_query = select(ProgressUpdate).filter(
                    ProgressUpdate.goal_id == goal.id
                ).order_by(ProgressUpdate.created_at.desc())
                progress_result = await db.execute(progress_query)
                latest_progress = progress_result.scalar_one_or_none()
                
                # Ensure progress_value is a valid number
                progress_value = 0
                if latest_progress and hasattr(latest_progress, 'progress_value'):
                    try:
                        progress_value = float(latest_progress.progress_value)
                        if not (0 <= progress_value <= 100):
                            progress_value = 0
                    except (TypeError, ValueError):
                        progress_value = 0
                
                formatted_goals.append({
                    "category": goal.category,
                    "description": goal.description,
                    "target_date": goal.target_date.isoformat() if goal.target_date else None,
                    "progress": progress_value,
                    "created_at": goal.created_at.isoformat() if goal.created_at else None
                })
            except Exception as e:
                logger.error(f"Error formatting goal {goal.id}: {str(e)}")
                continue  # Skip this goal if there's an error

        # If no goals yet, return starter suggestions
        if not goals:
            logger.info("No goals found, returning starter suggestions")
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "suggestions": [
                        "Start by creating your first SMART goal - make it Specific, Measurable, Achievable, Relevant, and Time-bound",
                        "Think about what you want to achieve in different areas of your life: Health, Career, Personal Development",
                        "Consider breaking down your future goals into smaller, manageable milestones"
                    ]
                }
            )

        # Use AI service to generate personalized suggestions
        ai_service = AIService()
        suggestions = await ai_service.get_personalized_suggestions(formatted_goals)
        
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
                "detail": str(e)
            }
        )

@router.get("/{goal_id}")
async def get_goal(
    goal_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_user_from_token)
) -> JSONResponse:
    try:
        # Find goal
        goal = await db.get(Goal, goal_id)
        if not goal:
            return JSONResponse(
                status_code=404,
                content={"success": False, "detail": "Goal not found"}
            )
        
        # Verify ownership
        if goal.user_id != current_user.id:
            return JSONResponse(
                status_code=403,
                content={"success": False, "detail": "Not authorized"}
            )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "goal": {
                    "id": goal.id,
                    "category": goal.category,
                    "description": goal.description,
                    "target_date": goal.target_date.isoformat(),
                    "created_at": goal.created_at.isoformat()
                }
            }
        )
    except Exception as e:
        logger.error(f"Error fetching goal: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": str(e)}
        )

@router.put("/update")
async def update_goal(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_user_from_token)
) -> JSONResponse:
    try:
        data = await request.json()
        goal = await db.get(Goal, data['id'])
        
        if not goal:
            return JSONResponse(
                status_code=404,
                content={"success": False, "detail": "Goal not found"}
            )
        
        if goal.user_id != current_user.id:
            return JSONResponse(
                status_code=403,
                content={"success": False, "detail": "Not authorized"}
            )

        if 'category' in data:
            goal.category = data['category']
        if 'description' in data:
            goal.description = data['description']
        if 'target_date' in data:
            goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()

        await db.commit()
        await db.refresh(goal)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "goal": {
                    "id": goal.id,
                    "category": goal.category,
                    "description": goal.description,
                    "target_date": goal.target_date.isoformat(),
                    "created_at": goal.created_at.isoformat()
                }
            }
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating goal: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": str(e)}
        )

@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_user_from_token)
) -> JSONResponse:
    try:
        goal = await db.get(Goal, goal_id)
        if not goal:
            return JSONResponse(
                status_code=404,
                content={"success": False, "detail": "Goal not found"}
            )
        
        if goal.user_id != current_user.id:
            return JSONResponse(
                status_code=403,
                content={"success": False, "detail": "Not authorized"}
            )

        await db.delete(goal)
        await db.commit()
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Goal deleted successfully"
            }
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting goal: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": str(e)}
        )