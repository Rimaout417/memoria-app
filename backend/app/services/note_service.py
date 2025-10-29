# Note business logic and CRUD operations
from app.schemas.note_schema import NoteCreate, NoteUpdate
from app.database import database
from app.models.note import Note
from sqlalchemy import select, insert, update, delete


async def create_note(payload: NoteCreate, user_id: int):
    """ノート作成"""
    query = (
        insert(Note.__table__)
        .values(title=payload.title, content=payload.content, user_id=user_id)
        .returning(Note.__table__)
    )
    return await database.fetch_one(query=query)


async def get_note(note_id: int, user_id: int):
    """ノート取得（自分のノートのみ）"""
    query = select(Note.__table__).where(Note.id == note_id, Note.user_id == user_id)
    return await database.fetch_one(query=query)


async def get_all_notes(user_id: int):
    """全ノート取得（自分のノートのみ）"""
    query = (
        select(Note.__table__)
        .where(Note.user_id == user_id)
        .order_by(Note.updated_date.desc())
    )
    return await database.fetch_all(query=query)


async def update_note(note_id: int, user_id: int, payload: NoteUpdate):
    """ノート更新"""
    values = {}
    if payload.title is not None:
        values["title"] = payload.title
    if payload.content is not None:
        values["content"] = payload.content

    if not values:
        return await get_note(note_id, user_id)

    query = (
        update(Note.__table__)
        .where(Note.id == note_id, Note.user_id == user_id)
        .values(**values)
        .returning(Note.__table__)
    )
    return await database.fetch_one(query=query)


async def delete_note(note_id: int, user_id: int):
    """ノート削除"""
    query = delete(Note.__table__).where(Note.id == note_id, Note.user_id == user_id)
    return await database.execute(query=query)


async def import_notes(notes_data: list, user_id: int):
    """ノートをインポート"""
    imported_count = 0
    for note_data in notes_data:
        # IDとuser_idを除外して、新しいノートとして作成
        query = (
            insert(Note.__table__)
            .values(
                title=note_data.get("title", "Untitled"),
                content=note_data.get("content", ""),
                user_id=user_id,
            )
            .returning(Note.__table__)
        )
        await database.fetch_one(query=query)
        imported_count += 1
    return imported_count
