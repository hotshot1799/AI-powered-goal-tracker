from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from services.goals import GoalService
from database import get_db
from api.v1.deps import get_current_user
from models import User

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

@router.get("/{goal_id}")
async def get_goal_details(
    goal_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        # Get user_id from session and convert to integer
        user_id_str = request.session.get('user_id')
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        try:
            user_id = int(user_id_str)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid user ID")

        # Fetch goal with proper type comparison
        goal_query = (
            select(Goal)
            .filter(
                Goal.id == goal_id,
                Goal.user_id == user_id  # Now both are integers
            )
        )
        result = await db.execute(goal_query)
        goal = result.scalar_one_or_none()

        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")

        # Fetch progress updates
        progress_query = (
            select(ProgressUpdate)
            .filter(ProgressUpdate.goal_id == goal_id)
            .order_by(ProgressUpdate.created_at.desc())
        )
        progress_result = await db.execute(progress_query)
        progress_updates = progress_result.scalars().all()

        # Get latest progress
        latest_progress = 0
        if progress_updates:
            latest_progress = progress_updates[0].progress_value

        return {
            "success": True,
            "goal": {
                "id": goal.id,
                "category": goal.category,
                "description": goal.description,
                "target_date": goal.target_date.isoformat(),
                "created_at": goal.created_at.isoformat(),
                "progress": latest_progress
            },
            "progress_updates": [
                {
                    "text": update.update_text,
                    "progress": update.progress_value,
                    "analysis": update.analysis,
                    "created_at": update.created_at.isoformat()
                }
                for update in progress_updates
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching goal details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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

@router.get("/suggestions/{user_id}")
async def get_suggestions(
    user_id: int, 
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        if not request.session.get('user_id'):
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Get user's goals for context
        query = select(Goal).filter(Goal.user_id == user_id)
        result = await db.execute(query)
        goals = result.scalars().all()
        
        ai_service = AIService()
        
        # If no goals yet, get starter suggestions
        if not goals:
            return {
                "success": True,
                "suggestions": [
                    "Start by creating a SMART goal - Specific, Measurable, Achievable, Relevant, and Time-bound",
                    "Consider breaking down your future goals into smaller, manageable tasks",
                    "Set up regular check-ins to track your progress"
                ]
            }

        # Create goals context for AI
        goals_analysis = "\n".join([
            f"Goal {i+1}:"
            f"\nCategory: {goal.category}"
            f"\nDescription: {goal.description}"
            f"\nTarget Date: {goal.target_date}"
            for i, goal in enumerate(goals)
        ])
        
        analysis_prompt = f"""
        Based on these goals:
        {goals_analysis}

        Provide 3 specific, actionable suggestions that:
        1. Address immediate next steps for achieving these goals
        2. Suggest ways to track progress effectively
        3. Offer strategies to overcome potential challenges

        Make each suggestion directly related to the user's goals.
        Format as a numbered list.
        Each suggestion should be specific to the goals mentioned.
        """
        
        try:
            suggestions_text = await ai_service.analyze_data(analysis_prompt)
            suggestions = [
                s.strip() for s in suggestions_text.split('\n') 
                if s.strip() and not s.startswith(('1.', '2.', '3.'))
            ][:3]
            
            if len(suggestions) < 3:
                raise ValueError("Insufficient AI suggestions generated")
                
        except Exception as ai_error:
            logging.error(f"AI analysis error: {str(ai_error)}")
            suggestions = [
                f"For your {goals[0].category} goal: Break down '{goals[0].description}' into weekly milestones",
                "Set up a daily tracking system for each of your goals",
                "Schedule weekly review sessions to assess your progress"
            ]
        
        return {
            "success": True,
            "suggestions": suggestions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
