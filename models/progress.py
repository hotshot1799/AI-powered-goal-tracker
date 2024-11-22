from sqlalchemy import Column, Integer, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class ProgressUpdate(Base):
    __tablename__ = "progress_updates"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    update_text = Column(Text, nullable=False)
    progress_value = Column(Float, default=0)
    analysis = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    goal = relationship("Goal", back_populates="progress_updates")
