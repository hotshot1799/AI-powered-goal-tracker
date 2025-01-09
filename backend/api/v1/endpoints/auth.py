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
import json
import time


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register")
async def register(request: Request, db: AsyncSession = Depends(get_db)):
    logger.info("Registration endpoint called")
    try:
        # Get request body
        body_bytes = await request.body()
        body_str = body_bytes.decode()
        logger.info(f"Received request body: {body_str}")
        
        # Parse JSON data
        data = json.loads(body_str)
        logger.info(f"Parsed request data: {data}")

        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                logger.error(f"Missing required field: {field}")
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "detail": f"Missing required field: {field}"
                    }
                )

        # Check if username exists
        username_query = select(User).filter(User.username == data['username'])
        username_result = await db.execute(username_query)
        if username_result.scalar_one_or_none():
            logger.warning(f"Username already exists: {data['username']}")
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
            logger.warning(f"Email already exists: {data['email']}")
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
        
        # Add to database
        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            logger.info(f"Successfully created user: {new_user.username}")
            
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

        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            await db.rollback()
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "detail": "Database error during registration"
                }
            )

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "detail": "Invalid JSON data"
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "detail": "An unexpected error occurred"
            }
        )

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    logger.info("Login attempt started")
    try:
        # Get request body
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
            logger.warning(f"Failed login attempt for username: {username}")
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "detail": "Incorrect username or password"
                }
            )

        # Create new session data
        request.session.clear()  # Clear synchronously
        request.session["user_id"] = str(user.id)
        request.session["username"] = user.username
        request.session["_session_expire_at"] = int(time.time()) + (3600 * 24)  # 24 hours

        logger.info(f"Session data set: {dict(request.session)}")
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "redirect": "/dashboard"
            }
        )

        # Set cookie explicitly
        cookie_value = request.session.get("session", "")
        if cookie_value:
            response.set_cookie(
                key="session",
                value=cookie_value,
                httponly=True,
                secure=True,
                samesite="none",
                max_age=86400  # 24 hours
            )

        logger.info(f"Login successful for user: {username}")
        await db.commit()
        return response

    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        await db.rollback()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "detail": "Login failed"
            }
        )

# Add debug endpoint
@router.get("/debug-session")
async def debug_session(request: Request):
    """Debug endpoint to check session state"""
    return {
        "session_data": dict(request.session),
        "cookies": dict(request.cookies),
        "headers": dict(request.headers)
    }

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

@router.get("/me")
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    logger.info("Checking current user session")
    logger.info(f"Session contents: {dict(request.session)}")
    logger.info(f"Cookies: {request.cookies}")
    
    try:
        user_id = request.session.get("user_id")
        logger.info(f"Session user_id: {user_id}")
        
        if not user_id:
            logger.warning("No user_id in session")
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
            logger.warning(f"User not found for id: {user_id}")
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "detail": "User not found"
                }
            )

        logger.info(f"User found: {user.username}")
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }
        )

    except Exception as e:
        logger.error(f"Error fetching current user: {str(e)}", exc_info=True)
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