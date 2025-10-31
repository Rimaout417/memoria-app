# AI Generation Pydantic schemas
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from datetime import datetime


class AIGenerationRequest(BaseModel):
    note_ids: List[int] = Field(..., min_length=1, max_length=10)
    prompt: Optional[str] = Field(None, max_length=2000)
    ai_provider: Literal["openai", "anthropic", "gemini"] = "openai"

    @field_validator("note_ids")
    @classmethod
    def validate_note_ids(cls, v):
        if not v:
            raise ValueError("At least one note_id is required")
        if len(v) != len(set(v)):
            raise ValueError("Duplicate note_ids are not allowed")
        return v


class AIGenerationResponse(BaseModel):
    id: int
    generated_content: str
    ai_provider: str
    note_ids: List[int]
    prompt: str
    created_date: datetime

    class ConfigDict:
        from_attributes = True


class SaveAsNoteRequest(BaseModel):
    generation_id: int
    title: str = Field(..., min_length=1, max_length=200)


class GenerationListResponse(BaseModel):
    items: List[AIGenerationResponse]
    total: int
    page: int
    per_page: int
