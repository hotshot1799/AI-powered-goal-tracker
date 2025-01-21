from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User
from schemas.user import UserCreate, PasswordResetRequest
from services.auth import AuthService
from core.security import create_access_token, get_password_hash, decode_token
from database import get_db
import smtplib
from email.mime.text import MIMEText
import os

router = APIRouter()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

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

@router.post("/request-password-reset")
async def request_password_reset(request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    query = select(User).filter(User.email == request.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        return JSONResponse(status_code=404, content={"success": False, "detail": "User not found"})
    
    token = create_access_token(subject=user.email)
    reset_link = f"https://yourfrontend.com/reset-password?token={token}"
    
    email_body = f"""
    <p>Click the link below to reset your password:</p>
    <a href='{reset_link}'>Reset Password</a>
    """
    
    try:
        await send_email(user.email, "Password Reset Request", email_body)
    except ValueError as e:
        return JSONResponse(status_code=500, content={"success": False, "detail": str(e)})
    
    return JSONResponse(status_code=200, content={"success": True, "message": "Password reset email sent"})

@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db: AsyncSession = Depends(get_db)):
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
        
        user.hashed_password = get_password_hash(new_password)
        await db.commit()
        
        return JSONResponse(status_code=200, content={"success": True, "message": "Password has been reset successfully"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Invalid token or expired"})
