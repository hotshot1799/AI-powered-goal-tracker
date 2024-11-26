from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User
from schemas.user import UserCreate, UserResponse, Token
from services.auth import AuthService
from core.security import create_access_token, get_password_hash
from database import get_db
from typing import Dict, Any
from datetime import timedelta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=Dict[str, Any])
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        # Check if user exists
        query = select(User).filter(
            (User.username == user_data.username) | 
            (User.email == user_data.email)
        )
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return {
            "success": True,
            "message": "Registration successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@router.post("/login", response_model=Dict[str, Any])
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing username or password"
            )

        # Find user
        query = select(User).filter(User.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not user.verify_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # Create access token with username as subject
        access_token = create_access_token(
            subject=user.username,
            extra_data={"user_id": user.id}
        )

        # Set session data
        request.session["user_id"] = str(user.id)
        request.session["username"] = user.username

        return {
            "success": True,
            "user_id": user.id,
            "username": user.username,
            "access_token": access_token,
            "token_type": "bearer",
            "redirect": "/dashboard"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/logout")
async def logout(request: Request) -> Dict[str, Any]:
    try:
        request.session.clear()
        return {
            "success": True,
            "message": "Logged out successfully",
            "redirect": "/login"
        }
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        # Find user
        query = select(User).filter(User.id == int(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user details"
        )

@router.put("/update", response_model=Dict[str, Any])
async def update_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        data = await request.json()
        
        # Find user
        query = select(User).filter(User.id == int(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update user data
        if 'username' in data:
            # Check if username is taken
            username_check = await db.execute(
                select(User).filter(
                    User.username == data['username'],
                    User.id != user.id
                )
            )
            if username_check.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            user.username = data['username']
            request.session["username"] = data['username']

        if 'email' in data:
            # Check if email is taken
            email_check = await db.execute(
                select(User).filter(
                    User.email == data['email'],
                    User.id != user.id
                )
            )
            if email_check.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )
            user.email = data['email']

        if 'password' in data:
            user.hashed_password = get_password_hash(data['password'])

        await db.commit()
        await db.refresh(user)

        return {
            "success": True,
            "message": "User updated successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )

@router.delete("/delete", response_model=Dict[str, Any])
async def delete_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        # Find user
        query = select(User).filter(User.id == int(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Delete user
        await db.delete(user)
        await db.commit()
        request.session.clear()

        return {
            "success": True,
            "message": "User deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )
