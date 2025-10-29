# Note Pydantic schemas
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    created_date: datetime
    updated_date: datetime

    class ConfigDict:
        from_attributes = True
