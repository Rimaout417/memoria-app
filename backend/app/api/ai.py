# AI API routes
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas.ai_schema import (
    AIGenerationRequest,
    AIGenerationResponse,
    SaveAsNoteRequest,
    GenerationListResponse,
)
from app.schemas.note_schema import NoteResponse
from app.services import ai_service
from app.core.security import get_current_user
from typing import Optional

router = APIRouter(prefix="/api/ai", tags=["ai"])

# レート制限の設定
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/generate-idea",
    response_model=AIGenerationResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/hour")
async def generate_idea(
    request: Request,
    payload: AIGenerationRequest,
    current_user=Depends(get_current_user),
):
    """
    AIを使用してアイデアを生成

    - **note_ids**: 選択されたノートIDのリスト（1-10個）
    - **prompt**: カスタムプロンプト（オプション、最大2000文字）
    - **ai_provider**: AIプロバイダー（openai, anthropic, gemini）

    レート制限: 1時間あたり10回
    """
    try:
        result = await ai_service.generate_idea(
            note_ids=payload.note_ids,
            user_id=current_user["id"],
            prompt=payload.prompt,
            ai_provider=payload.ai_provider,
        )
        return result
    except HTTPException:
        # ai_serviceから投げられたHTTPExceptionをそのまま再送出
        raise
    except Exception as e:
        # 予期しないエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@router.get(
    "/generations",
    response_model=GenerationListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_generations(
    page: int = 1,
    per_page: int = 20,
    current_user=Depends(get_current_user),
):
    """
    AI生成履歴を取得

    - **page**: ページ番号（デフォルト: 1）
    - **per_page**: 1ページあたりの件数（デフォルト: 20）

    作成日時の降順で返されます
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be greater than 0",
        )

    if per_page < 1 or per_page > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Per page must be between 1 and 100",
        )

    result = await ai_service.get_generations(
        user_id=current_user["id"],
        page=page,
        per_page=per_page,
    )
    return result


@router.post(
    "/save-as-note",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_as_note(
    payload: SaveAsNoteRequest,
    current_user=Depends(get_current_user),
):
    """
    生成結果を新しいノートとして保存（オプション機能）

    - **generation_id**: 生成履歴のID
    - **title**: ノートのタイトル（1-200文字）
    """
    result = await ai_service.save_generation_as_note(
        generation_id=payload.generation_id,
        user_id=current_user["id"],
        title=payload.title,
    )
    return result
