# Favorite Pydantic schemas
from pydantic import BaseModel
from datetime import datetime


class FavoriteCreate(BaseModel):
    note_id: int


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    note_id: int
    created_date: datetime

    class ConfigDict:
        from_attributes = True
