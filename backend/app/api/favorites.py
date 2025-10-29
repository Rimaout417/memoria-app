# Favorites API routes
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.favorite_schema import FavoriteCreate, FavoriteResponse
from app.schemas.note_schema import NoteResponse
from app.services import favorite_service
from app.core.security import get_current_user
from typing import List

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.post("", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(payload: FavoriteCreate, current_user=Depends(get_current_user)):
    """お気に入り追加"""
    favorite = await favorite_service.add_favorite(payload, current_user["id"])
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return favorite


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(note_id: int, current_user=Depends(get_current_user)):
    """お気に入り削除"""
    result = await favorite_service.remove_favorite(note_id, current_user["id"])
    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found"
        )
    return None


@router.get("", response_model=List[NoteResponse])
async def get_favorites(current_user=Depends(get_current_user)):
    """お気に入り一覧取得"""
    favorites = await favorite_service.get_favorites(current_user["id"])
    return favorites


@router.get("/{note_id}/check")
async def check_favorite(note_id: int, current_user=Depends(get_current_user)):
    """お気に入りかどうか確認"""
    is_fav = await favorite_service.is_favorite(note_id, current_user["id"])
    return {"is_favorite": is_fav}
