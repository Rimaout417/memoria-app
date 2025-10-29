from contextlib import asynccontextmanager
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import notes, users, auth, favorites
from app.database import database, engine, Base
from app.models.user import User
from app.models.note import Note
from app.models.favorite import Favorite

# テーブル作成
Base.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await database.connect()

    # カラー出力（Windowsでも動作）
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

    message = f"""
{GREEN}{'='*60}
🚀 Memoria API Server Started!
{'='*60}{RESET}

{BLUE}📚 Swagger UI:{RESET}  http://localhost:8000/docs
{BLUE}📖 ReDoc:{RESET}       http://localhost:8000/redoc

{BLUE}🔐 Auth:{RESET}
  - POST /api/auth/register
  - POST /api/auth/login
  - GET  /api/auth/me

{BLUE}📝 Notes:{RESET}
  - GET/POST    /api/notes
  - GET/PUT/DEL /api/notes/{{id}}

{BLUE}⭐ Favorites:{RESET}
  - GET         /api/favorites
  - POST        /api/favorites
  - DELETE      /api/favorites/{{note_id}}
  - GET         /api/favorites/{{note_id}}/check

{GREEN}{'='*60}{RESET}
"""
    print(message, file=sys.stderr)
    yield

    # Shutdown
    await database.disconnect()


app = FastAPI(
    title="Memoria API",
    description="Note-taking application with user authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # React/Viteの開発サーバー
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notes.router)
app.include_router(favorites.router)


@app.get("/")
async def root():
    """ヘルスチェック"""
    return {"message": "Memoria API is running", "docs": "/docs", "version": "1.0.0"}
