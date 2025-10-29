# Notes API routes
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.note_schema import NoteCreate, NoteUpdate, NoteResponse
from app.services import note_service
from app.core.security import get_current_user
from typing import List

router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(payload: NoteCreate, current_user=Depends(get_current_user)):
    """ノート作成"""
    note = await note_service.create_note(payload, current_user["id"])
    return note


@router.get("", response_model=List[NoteResponse])
async def get_notes(current_user=Depends(get_current_user)):
    """ノート一覧取得"""
    notes = await note_service.get_all_notes(current_user["id"])
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, current_user=Depends(get_current_user)):
    """ノート詳細取得"""
    note = await note_service.get_note(note_id, current_user["id"])
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int, payload: NoteUpdate, current_user=Depends(get_current_user)
):
    """ノート更新"""
    note = await note_service.update_note(note_id, current_user["id"], payload)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int, current_user=Depends(get_current_user)):
    """ノート削除"""
    result = await note_service.delete_note(note_id, current_user["id"])
    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return None


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_notes(notes_data: List[dict], current_user=Depends(get_current_user)):
    """ノートをインポート"""
    if not notes_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No notes to import"
        )

    imported_count = await note_service.import_notes(notes_data, current_user["id"])
    return {
        "message": f"{imported_count} notes imported successfully",
        "count": imported_count,
    }
