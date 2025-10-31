# AIGeneration SQLAlchemy model
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.sql import func
from app.database import Base


class AIGeneration(Base):
    __tablename__ = "ai_generations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    note_ids = Column(ARRAY(Integer), nullable=False)
    prompt = Column(Text, nullable=False)
    ai_provider = Column(String(50), nullable=False)
    generated_content = Column(Text, nullable=False)
    created_date = Column(DateTime, default=func.now(), nullable=False)
