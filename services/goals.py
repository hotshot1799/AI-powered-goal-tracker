from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalUpdate
from app.core.exceptions import NotFoundException
from typing import List

class GoalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_goal(self, user_id: int, goal_data: GoalCreate) -> Goal:
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

    async def get_user_goals(self, user_id: int) -> List[Goal]:
        query = select(Goal).filter(Goal.user_id == user_id)
        result = await self.db.execute(query)
        goals = result.scalars().all()
        return goals
