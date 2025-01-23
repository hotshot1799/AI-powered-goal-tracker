from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import JSONResponse
from models import User
from schemas.user import UserCreate, UserResponse, Token
from services.auth import AuthService
from core.security import verify_password, get_password_hash, create_access_token, decode_token
from core.config import settings
from database import get_db
from typing import Dict, Any
import logging
import json
import smtplib
from email.mime.text import MIMEText
import os

router = APIRouter()
logger = logging.getLogger(__name__)

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://ai-powered-goal-tracker-z0co.onrender.com")

async def send_email(to_email: str, subject: str, body: str):
    logger.info(f"Attempting to send email to: {to_email}")
    
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = settings.SENDER_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"SMTP error: {str(e)}")
        raise ValueError(f"Failed to send email: {str(e)}")

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
    <a href="{verification_link}">{verification_link}</a>
    """
    
    await send_email(new_user.email, "Verify Your Email", email_body)
    return JSONResponse(status_code=201, content={"success": True, "message": "Registration successful. Check your email for verification."})

@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        query = select(User).filter(User.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_verified:
            return {"success": True, "message": "Email already verified"}

        user.is_verified = True
        await db.commit()
        return {"success": True, "message": "Email verified successfully"}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

@router.post("/login")
async def login(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    query = select(User).filter(User.username == data["username"])
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(data["password"], user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    token = create_access_token(subject=user.email)
    return {"success": True, "token": token, "user_id": user.id, "username": user.username}

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"success": True, "message": "Logged out successfully"}

@router.get("/me")
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    query = select(User).filter(User.id == int(user_id))
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"success": True, "user": {"id": user.id, "username": user.username, "email": user.email}}

@router.put("/update")
async def update_user(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    data = await request.json()
    query = select(User).filter(User.id == int(user_id))
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if "username" in data:
        user.username = data["username"]
    if "email" in data:
        user.email = data["email"]
    if "password" in data:
        user.hashed_password = get_password_hash(data["password"])

    await db.commit()
    await db.refresh(user)
    return {"success": True, "message": "User updated successfully"}

@router.delete("/delete")
async def delete_user(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    query = select(User).filter(User.id == int(user_id))
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    request.session.clear()
    return {"success": True, "message": "User deleted successfully"}
