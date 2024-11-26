from datetime import datetime, timedelta
from typing import Any, Union, Optional, Dict
from jose import jwt
from passlib.context import CryptContext
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    extra_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a new access token.
    
    Args:
        subject: The subject of the token (usually user_id or username)
        expires_delta: Optional expiration time delta
        extra_data: Optional additional data to include in the token
    
    Returns:
        str: The encoded JWT token
    """
    to_encode = {}
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "sub": str(subject)
    })
    
    if extra_data:
        to_encode.update(extra_data)
    
    return jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm="HS256"
    )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def decode_token(token: str) -> dict:
    """Decode a JWT token."""
    return jwt.decode(
        token, 
        settings.SECRET_KEY, 
        algorithms=["HS256"]
    )
