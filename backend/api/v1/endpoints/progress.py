# backend/api/v1/endpoints/progress.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import ProgressUpdate, Goal, User
from services.ai import AIService
from typing import Dict, Any
import logging
from core.security import decode_token

router = APIRouter()
logger = logging.getLogger(__name__)

async def get_user_from_token(request: Request, db: AsyncSession) -> User:
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        query = select(User).filter(User.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.post("/{goal_id}")
async def update_progress(
    goal_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        current_user = await get_user_from_token(request, db)
        data = await request.json()
        update_text = data.get('update_text')
        
        if not update_text:
            raise HTTPException(status_code=400, detail="Update text required")

        # Verify goal ownership and get goal details
        goal = await db.get(Goal, goal_id)
        if not goal or goal.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Goal not found")

        # Use AI to analyze progress
        ai_service = AIService()
        analysis_result = await ai_service.analyze_progress(update_text, goal.description)

        progress_update = ProgressUpdate(
            goal_id=goal_id,
            update_text=update_text,
            progress_value=analysis_result['percentage'],
            analysis=analysis_result['analysis']
        )

        db.add(progress_update)
        await db.commit()
        await db.refresh(progress_update)

        return {
            "success": True,
            "update": {
                "id": progress_update.id,
                "text": progress_update.update_text,
                "progress": progress_update.progress_value,
                "analysis": progress_update.analysis,
                "created_at": progress_update.created_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Progress update error: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{goal_id}")
async def get_progress_history(
    goal_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        current_user = await get_user_from_token(request, db)

        # Verify goal ownership
        goal = await db.get(Goal, goal_id)
        if not goal or goal.user_id != current_user.id:
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
                "id": update.id,
                "text": update.update_text,
                "progress": update.progress_value,
                "analysis": update.analysis,
                "created_at": update.created_at.isoformat()
            } for update in updates]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching progress updates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))