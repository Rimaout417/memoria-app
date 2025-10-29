# Favorite business logic and CRUD operations
from app.schemas.favorite_schema import FavoriteCreate
from app.database import database
from app.models.favorite import Favorite
from app.models.note import Note
from sqlalchemy import select, insert, delete, join


async def add_favorite(payload: FavoriteCreate, user_id: int):
    """お気に入り追加"""
    # ノートが存在するか確認
    note_query = select(Note.__table__).where(Note.id == payload.note_id)
    note = await database.fetch_one(query=note_query)
    if not note:
        return None

    # 既にお気に入りに追加されているか確認
    existing_query = select(Favorite.__table__).where(
        Favorite.user_id == user_id, Favorite.note_id == payload.note_id
    )
    existing = await database.fetch_one(query=existing_query)
    if existing:
        return existing

    # お気に入り追加
    query = (
        insert(Favorite.__table__)
        .values(user_id=user_id, note_id=payload.note_id)
        .returning(Favorite.__table__)
    )
    return await database.fetch_one(query=query)


async def remove_favorite(note_id: int, user_id: int):
    """お気に入り削除"""
    query = delete(Favorite.__table__).where(
        Favorite.user_id == user_id, Favorite.note_id == note_id
    )
    return await database.execute(query=query)


async def get_favorites(user_id: int):
    """お気に入り一覧取得（ノート情報も含む）"""
    # JOINしてノート情報を取得
    query = (
        select(Note.__table__)
        .select_from(
            join(Favorite.__table__, Note.__table__, Favorite.note_id == Note.id)
        )
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_date.desc())
    )
    return await database.fetch_all(query=query)


async def is_favorite(note_id: int, user_id: int):
    """お気に入りかどうか確認"""
    query = select(Favorite.__table__).where(
        Favorite.user_id == user_id, Favorite.note_id == note_id
    )
    result = await database.fetch_one(query=query)
    return result is not None
