# AI Service - Business logic for AI idea generation
import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import select, insert, desc, func
from app.database import database
from app.models.note import Note
from app.models.ai_generation import AIGeneration
from app.services.ai_providers.factory import get_ai_provider
from app.core.config import settings

logger = logging.getLogger(__name__)


async def get_notes_for_context(note_ids: List[int], user_id: int) -> List[dict]:
    """
    複数のノートIDから各ノートのコンテンツを取得
    ユーザー所有権を検証

    Args:
        note_ids: ノートIDのリスト
        user_id: ユーザーID

    Returns:
        ノートのリスト

    Raises:
        HTTPException: ノートが見つからない、またはアクセス権限がない場合
    """
    # 複数のノートを一度に取得（ユーザー所有権も同時に検証）
    query = select(Note.__table__).where(Note.id.in_(note_ids), Note.user_id == user_id)
    notes = await database.fetch_all(query=query)

    # 取得したノートのIDリストを作成
    found_note_ids = {note["id"] for note in notes}

    # リクエストされたすべてのノートが見つかったか確認
    missing_note_ids = set(note_ids) - found_note_ids
    if missing_note_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notes not found or access denied: {sorted(missing_note_ids)}",
        )

    return notes


def build_context_from_notes(notes: List[dict]) -> str:
    """
    ノートコンテンツを結合してAI用のコンテキストを構築

    Args:
        notes: ノートのリスト

    Returns:
        結合されたコンテキスト文字列
    """
    if not notes:
        return ""

    # ノートのタイトルとコンテンツを整形して結合
    context_parts = []
    for note in notes:
        context_parts.append(f"# {note['title']}\n\n{note['content']}")

    return "\n\n---\n\n".join(context_parts)


async def call_ai_with_retry(
    provider_name: str, prompt: str, context: str, max_retries: int = 3
) -> str:
    """
    AIプロバイダーを呼び出し、エラー時にリトライを実行

    Args:
        provider_name: AIプロバイダー名
        prompt: プロンプト
        context: コンテキスト
        max_retries: 最大リトライ回数

    Returns:
        生成されたコンテンツ

    Raises:
        HTTPException: AI APIエラー
    """
    provider = None
    last_error = None

    for attempt in range(max_retries):
        try:
            # プロバイダーインスタンスを取得
            if provider is None:
                try:
                    provider = get_ai_provider(provider_name)
                except ValueError as e:
                    logger.error(f"AI provider configuration error: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="AI サービスの設定エラー",
                    )

            # タイムアウト付きでAI APIを呼び出し
            generated_content = await asyncio.wait_for(
                provider.generate(prompt, context),
                timeout=settings.AI_REQUEST_TIMEOUT,
            )

            return generated_content

        except asyncio.TimeoutError:
            logger.error(
                f"AI API timeout on attempt {attempt + 1}/{max_retries} for provider {provider_name}"
            )
            last_error = HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="AI サービスのリクエストがタイムアウトしました",
            )

            # タイムアウトはリトライしない
            raise last_error

        except Exception as e:
            error_message = str(e).lower()
            logger.error(
                f"AI API error on attempt {attempt + 1}/{max_retries}: {str(e)}"
            )

            # トークン制限エラーの検出
            if any(
                keyword in error_message
                for keyword in ["token", "length", "too long", "context_length"]
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="選択したノートの内容が長すぎます",
                )

            # 5xxエラーまたはサービス利用不可エラーの検出
            if any(
                keyword in error_message
                for keyword in [
                    "503",
                    "500",
                    "502",
                    "504",
                    "unavailable",
                    "overloaded",
                    "rate limit",
                ]
            ):
                last_error = HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI サービスが一時的に利用できません",
                )

                # 最後の試行でない場合はリトライ（エクスポネンシャルバックオフ）
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # 1秒、2秒、4秒
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise last_error

            # その他のエラー
            last_error = HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI サービスでエラーが発生しました: {str(e)}",
            )

            # リトライしない
            raise last_error

    # すべてのリトライが失敗した場合
    if last_error:
        raise last_error

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="AI サービスでエラーが発生しました",
    )


async def generate_idea(
    note_ids: List[int],
    user_id: int,
    prompt: Optional[str] = None,
    ai_provider: str = "openai",
) -> Dict[str, Any]:
    """
    AIを使用してアイデアを生成

    Args:
        note_ids: ノートIDのリスト
        user_id: ユーザーID
        prompt: カスタムプロンプト（オプション）
        ai_provider: AIプロバイダー名

    Returns:
        生成結果の辞書

    Raises:
        ValueError: 無効なパラメータ
        HTTPException: ノートが見つからない、AI APIエラー
    """
    # ノート取得とユーザー所有権検証
    notes = await get_notes_for_context(note_ids, user_id)

    # コンテキスト構築
    context = build_context_from_notes(notes)

    # デフォルトプロンプトの設定
    if not prompt:
        prompt = "これらのノートから新しいアイデアを生成してください"

    # AIプロバイダーを使用してアイデア生成（リトライ付き）
    generated_content = await call_ai_with_retry(
        ai_provider, prompt, context, max_retries=settings.AI_MAX_RETRIES
    )

    # 生成履歴をデータベースに保存
    query = insert(AIGeneration.__table__).values(
        user_id=user_id,
        note_ids=note_ids,
        prompt=prompt,
        ai_provider=ai_provider,
        generated_content=generated_content,
    )
    generation_id = await database.execute(query=query)

    # 保存した履歴を取得して返す
    select_query = select(AIGeneration.__table__).where(
        AIGeneration.id == generation_id
    )
    generation = await database.fetch_one(query=select_query)

    return dict(generation)


async def get_generations(
    user_id: int, page: int = 1, per_page: int = 20
) -> Dict[str, Any]:
    """
    ユーザーのAI生成履歴を取得

    Args:
        user_id: ユーザーID
        page: ページ番号
        per_page: 1ページあたりの件数

    Returns:
        ページネーション付き生成履歴
    """
    # ページネーションのオフセット計算
    offset = (page - 1) * per_page

    # 総件数を取得
    count_query = (
        select(func.count())
        .select_from(AIGeneration.__table__)
        .where(AIGeneration.user_id == user_id)
    )
    total = await database.fetch_val(query=count_query)

    # 生成履歴を取得（作成日時の降順）
    query = (
        select(AIGeneration.__table__)
        .where(AIGeneration.user_id == user_id)
        .order_by(desc(AIGeneration.created_date))
        .limit(per_page)
        .offset(offset)
    )
    generations = await database.fetch_all(query=query)

    return {
        "items": [dict(gen) for gen in generations],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


async def save_generation_as_note(
    generation_id: int, user_id: int, title: str
) -> Dict[str, Any]:
    """
    生成結果を新しいノートとして保存

    Args:
        generation_id: 生成ID
        user_id: ユーザーID
        title: ノートのタイトル

    Returns:
        作成されたノート

    Raises:
        HTTPException: 生成履歴が見つからない、またはアクセス権限がない場合
    """
    # 生成履歴を取得（ユーザー所有権も検証）
    query = select(AIGeneration.__table__).where(
        AIGeneration.id == generation_id, AIGeneration.user_id == user_id
    )
    generation = await database.fetch_one(query=query)

    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found or access denied",
        )

    # 新しいノートを作成
    insert_query = insert(Note.__table__).values(
        title=title,
        content=generation["generated_content"],
        user_id=user_id,
    )
    note_id = await database.execute(query=insert_query)

    # 作成したノートを取得して返す
    select_query = select(Note.__table__).where(Note.id == note_id)
    note = await database.fetch_one(query=select_query)

    return dict(note)
