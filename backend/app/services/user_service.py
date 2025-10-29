# User business logic and CRUD operations
from app.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.database import database
from app.models.user import User
from sqlalchemy import select, insert, update, delete


async def create_user(payload: UserCreate):
    """ユーザー作成（パスワードハッシュ化）"""
    password_hash = get_password_hash(payload.password)

    query = (
        insert(User.__table__)
        .values(username=payload.username, password_hash=password_hash, is_active=True)
        .returning(User.__table__)
    )

    return await database.fetch_one(query=query)


async def get_user(user_id: int):
    """ユーザー取得"""
    query = select(User.__table__).where(User.id == user_id)
    return await database.fetch_one(query=query)


async def get_by_username(username: str):
    """ユーザー名で検索"""
    query = select(User.__table__).where(User.username == username)
    return await database.fetch_one(query=query)


async def get_all_users():
    """全ユーザー取得"""
    query = select(User.__table__)
    return await database.fetch_all(query=query)


async def update_user(user_id: int, payload: UserUpdate):
    """ユーザー更新"""
    values = {}
    if payload.password:
        values["password_hash"] = get_password_hash(payload.password)
    if payload.is_active is not None:
        values["is_active"] = payload.is_active

    query = (
        update(User.__table__)
        .where(User.id == user_id)
        .values(**values)
        .returning(User.__table__)
    )
    return await database.fetch_one(query=query)


async def delete_user(user_id: int):
    """ユーザー削除"""
    query = delete(User.__table__).where(User.id == user_id)
    return await database.execute(query=query)


async def authenticate_user(username: str, password: str):
    """ユーザー認証"""
    user = await get_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user
