from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import verify_password
from typing import Optional

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        # Check if user exists
        query = select(User).filter(
            (User.username == user_data.username) | 
            (User.email == user_data.email)
        )
        result = await self.db.execute(query)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ValueError("Username or email already registered")

        # Create new user
        user = User(
            username=user_data.username,
            email=user_data.email
        )
        user.set_password(user_data.password)
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user

    async def authenticate_user(
        self, username: str, password: str
    ) -> Optional[User]:
        query = select(User).filter(User.username == username)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user or not user.verify_password(password):
            return None
        
        return user

    def create_access_token(self, data: dict) -> str:
        return create_access_token(data)
