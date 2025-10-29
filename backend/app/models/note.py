# Note SQLAlchemy model
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_date = Column(DateTime, default=func.now(), nullable=False)
    updated_date = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
