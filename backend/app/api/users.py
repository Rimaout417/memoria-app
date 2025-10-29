# User API routes
from fastapi import APIRouter, HTTPException, Path, Depends
from typing import List
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(payload: UserCreate):
    """新規ユーザー作成（管理者用）"""
    # ユーザー名の重複チェック
    existing_user = await user_service.get_by_username(payload.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = await user_service.create_user(payload)
    return user


@router.get("/{id}/", response_model=UserResponse)
async def read_user(id: int = Path(..., gt=0)):
    """ユーザー詳細取得"""
    user = await user_service.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=List[UserResponse])
async def read_all_users():
    """ユーザー一覧取得"""
    return await user_service.get_all_users()


@router.put("/{id}/", response_model=UserResponse)
async def update_user(
    payload: UserUpdate,
    id: int = Path(..., gt=0),
):
    """ユーザー情報更新"""
    user = await user_service.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await user_service.update_user(id, payload)
    return updated_user


@router.delete("/{id}/", response_model=UserResponse)
async def delete_user(id: int = Path(..., gt=0)):
    """ユーザー削除"""
    user = await user_service.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await user_service.delete_user(id)
    return user
