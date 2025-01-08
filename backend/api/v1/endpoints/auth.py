from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import JSONResponse
from models import User
from schemas.user import UserCreate, UserResponse, Token
from services.auth import AuthService
from core.security import create_access_token, get_password_hash
from database import get_db
from typing import Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register")
async def register(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get JSON data from request
        data = await request.json()
        logger.info(f"Received registration request for username: {data.get('username')}")

        # Check required fields
        required_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "detail": f"Missing required fields: {', '.join(missing_fields)}"
                }
            )

        # Check if username exists
        username_query = select(User).filter(User.username == data['username'])
        username_result = await db.execute(username_query)
        if username_result.scalar_one_or_none():
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "detail": "Username already exists"
                }
            )

        # Check if email exists
        email_query = select(User).filter(User.email == data['email'])
        email_result = await db.execute(email_query)
        if email_result.scalar_one_or_none():
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "detail": "Email already exists"
                }
            )

        # Create new user
        hashed_password = get_password_hash(data['password'])
        new_user = User(
            username=data['username'],
            email=data['email'],
            hashed_password=hashed_password
        )
        
        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
        except Exception as db_error:
            logger.error(f"Database error during user creation: {str(db_error)}")
            await db.rollback()
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "detail": "Database error during registration"
                }
            )

        logger.info(f"Successfully registered user: {new_user.username}")
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Registration successful",
                "user": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "email": new_user.email
                }
            }
        )

    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "detail": str(e)
            }
        )

@router.post("/login")
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "detail": "Missing username or password"
                }
            )

        # Find user
        query = select(User).filter(User.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not user.verify_password(password):
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "detail": "Incorrect username or password"
                }
            )

        # Set session data
        request.session["user_id"] = str(user.id)
        request.session["username"] = user.username

        return {
            "success": True,
            "user_id": user.id,
            "username": user.username,
            "redirect": "/dashboard"
        }

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "detail": "Login failed"
            }
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
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "detail": "Logout failed"
            }
        )

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "detail": "Not authenticated"
                }
            )

        # Find user
        query = select(User).filter(User.id == int(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "detail": "User not found"
                }
            )

        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }

    except Exception as e:
        logger.error(f"Error fetching current user: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "detail": "Error fetching user details"
            }
        )

@router.put("/update", response_model=Dict[str, Any])
async def update_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "detail": "Not authenticated"
                }
            )

        data = await request.json()
        
        # Find user
        query = select(User).filter(User.id == int(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "detail": "User not found"
                }
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
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "detail": "Username already taken"
                    }
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
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "detail": "Email already taken"
                    }
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

    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        await db.rollback()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "detail": "Error updating user"
            }
        )

@router.delete("/delete", response_model=Dict[str, Any])
async def delete_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "detail": "Not authenticated"
                }
            )

        # Find user
        query = select(User).filter(User.id == int(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "detail": "User not found"
                }
            )

        # Delete user
        await db.delete(user)
        await db.commit()
        request.session.clear()

        return {
            "success": True,
            "message": "User deleted successfully"
        }

    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        await db.rollback()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "detail": "Error deleting user"
            }
        )