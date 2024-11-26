from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import ProgressUpdate, Goal
from services.ai import AIService
from typing import Dict, Any
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/{goal_id}")
async def update_progress(
    goal_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        data = await request.json()
        update_text = data.get('update_text')
        if not update_text:
            raise HTTPException(status_code=400, detail="Update text required")

        # Verify goal ownership
        goal = await db.get(Goal, goal_id)
        if not goal or str(goal.user_id) != str(user_id):
            raise HTTPException(status_code=404, detail="Goal not found")

        # Use AI to analyze progress
        ai_service = AIService()
        analysis_prompt = f"""
        Goal: {goal.description}
        Category: {goal.category}
        Progress Update: {update_text}

        Based on this progress update, provide:
        1. A percentage (0-100) indicating goal completion progress
        2. A brief analysis explaining why this percentage was chosen
        
        Respond in JSON format:
        {{
            "percentage": number,
            "analysis": "brief explanation"
        }}
        """

        try:
            ai_response = await ai_service.analyze_data(analysis_prompt)
            ai_data = json.loads(ai_response)
            progress_value = float(ai_data.get('percentage', 0))
            analysis = ai_data.get('analysis', 'Progress analyzed')
            progress_value = max(0, min(100, progress_value))
        except Exception as ai_error:
            logger.error(f"AI analysis error: {str(ai_error)}")
            progress_value = 0
            analysis = "Unable to analyze progress"

        progress_update = ProgressUpdate(
            goal_id=goal_id,
            update_text=update_text,
            progress_value=progress_value,
            analysis=analysis
        )

        db.add(progress_update)
        await db.commit()
        await db.refresh(progress_update)

        return {
            "success": True,
            "update": {
                "text": update_text,
                "progress": progress_value,
                "analysis": analysis,
                "created_at": progress_update.created_at.isoformat()
            }
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Progress update error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{goal_id}")
async def get_progress_history(
    goal_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Verify goal ownership
        goal = await db.get(Goal, goal_id)
        if not goal or str(goal.user_id) != str(user_id):
            raise HTTPException(status_code=404, detail="Goal not found")

        # Get progress updates
        query = select(ProgressUpdate).filter(
            ProgressUpdate.goal_id == goal_id
        ).order_by(ProgressUpdate.created_at.desc())
        
        result = await db.execute(query)
        updates = result.scalars().all()

        return {
            "success": True,
            "updates": [{
                "text": update.update_text,
                "progress": update.progress_value,
                "analysis": update.analysis,
                "created_at": update.created_at.isoformat()
            } for update in updates]
        }

    except Exception as e:
        logger.error(f"Error fetching progress updates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
