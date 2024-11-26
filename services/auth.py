from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User
from schemas.user import UserCreate
from core.security import get_password_hash, verify_password, create_access_token
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> Dict[str, Any]:
        try:
            # Check if user exists
            query = select(User).filter(
                (User.username == user_data.username) | 
                (User.email == user_data.email)
            )
            result = await self.db.execute(query)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise ValueError("Username or email already registered")

            # Create new user with hashed password
            hashed_password = get_password_hash(user_data.password)
            user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": user.created_at
                }
            }
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            await self.db.rollback()
            raise

    async def authenticate_user(
        self, username: str, password: str
    ) -> Optional[Dict[str, Any]]:
        try:
            query = select(User).filter(User.username == username)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            
            if not user or not user.verify_password(password):
                return None

            return {
                "success": True,
                "user_id": user.id,
                "username": user.username
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise
