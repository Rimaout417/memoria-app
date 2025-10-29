from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


# ユーザー作成時のリクエスト
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)


# ユーザーログイン時のリクエスト
class UserLogin(BaseModel):
    username: str
    password: str


# ユーザー情報のレスポンス（パスワードは含めない）
class UserResponse(BaseModel):
    id: int
    username: str
    is_active: bool
    created_date: datetime

    class ConfigDict:
        from_attributes = True


# ユーザー更新時のリクエスト
class UserUpdate(BaseModel):
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


# ログイン成功時のトークンレスポンス
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# トークンのペイロード
class TokenData(BaseModel):
    username: Optional[str] = None
