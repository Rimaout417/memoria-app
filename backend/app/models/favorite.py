# Favorite SQLAlchemy model
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    created_date = Column(DateTime, default=func.now(), nullable=False)

    # ユーザーとノートの組み合わせは一意
    __table_args__ = (
        UniqueConstraint("user_id", "note_id", name="unique_user_note_favorite"),
    )
