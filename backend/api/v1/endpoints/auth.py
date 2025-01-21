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
import smtplib
from email.mime.text import MIMEText
import os

router = APIRouter()
logger = logging.getLogger(__name__)


SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://yourfrontend.com")

async def send_email(to_email: str, subject: str, body: str):
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        raise ValueError("SMTP credentials are not set.")
    
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = SMTP_USERNAME
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
    except smtplib.SMTPException as e:
        raise ValueError(f"SMTP error occurred: {str(e)}")

@router.post("/register")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).filter(User.email == user_data.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Email already registered"})

    hashed_password = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, email=user_data.email, hashed_password=hashed_password, is_verified=False)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token(subject=new_user.email)
    verification_link = f"{FRONTEND_URL}/verify-email?token={token}"
    email_body = f"""
    <p>Click the link below to verify your email:</p>
    <a href='{verification_link}'>Verify Email</a>
    """
    await send_email(new_user.email, "Email Verification", email_body)

    return JSONResponse(status_code=201, content={"success": True, "message": "Registration successful! Please check your email to verify your account."})

@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email:
            return JSONResponse(status_code=400, content={"success": False, "detail": "Invalid token"})

        query = select(User).filter(User.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            return JSONResponse(status_code=404, content={"success": False, "detail": "User not found"})

        if user.is_verified:
            return JSONResponse(status_code=200, content={"success": True, "message": "Email already verified"})

        user.is_verified = True
        await db.commit()

        return JSONResponse(status_code=200, content={"success": True, "message": "Email verified successfully"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Invalid token or expired"})

@router.post("/login")
async def login(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    query = select(User).filter(User.username == data["username"])
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(data["password"], user.hashed_password):
        return JSONResponse(status_code=401, content={"success": False, "detail": "Incorrect username or password"})

    if not user.is_verified:
        return JSONResponse(status_code=403, content={"success": False, "detail": "Email not verified. Please check your email."})

    token = create_access_token(subject=user.email)
    return JSONResponse(status_code=200, content={"success": True, "token": token})


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