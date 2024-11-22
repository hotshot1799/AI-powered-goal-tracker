from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from core.security import get_password_hash, verify_password

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    goals = relationship("Goal", back_populates="user")

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)

    def set_password(self, password: str) -> None:
        self.hashed_password = get_password_hash(password)
