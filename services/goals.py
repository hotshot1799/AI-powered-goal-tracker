from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.goal import Goal
from schemas.goal import GoalCreate, GoalUpdate
from typing import List
import logging

logger = logging.getLogger(__name__)

class GoalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_goal(self, user_id: int, goal_data: GoalCreate) -> Goal:
        try:
            goal = Goal(
                user_id=user_id,
                category=goal_data.category,
                description=goal_data.description,
                target_date=goal_data.target_date
            )
            
            self.db.add(goal)
            await self.db.commit()
            await self.db.refresh(goal)
            
            return goal
        except Exception as e:
            logger.error(f"Error creating goal: {str(e)}")
            raise

    async def get_user_goals(self, user_id: int) -> List[Goal]:
        try:
            query = select(Goal).filter(Goal.user_id == user_id)
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching goals: {str(e)}")
            raise
