from contextlib import asynccontextmanager
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api import notes, users, auth, favorites, ai
from app.database import database, engine, Base
from app.models.user import User
from app.models.note import Note
from app.models.favorite import Favorite
from app.models.ai_generation import AIGeneration

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

{BLUE}🤖 AI Generation:{RESET}
  - POST        /api/ai/generate-idea
  - GET         /api/ai/generations
  - POST        /api/ai/save-as-note

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

# レート制限の設定
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS設定（フロントエンドからのアクセスを許可）
from app.core.config import settings

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

# 本番環境のフロントエンドURLを追加
if settings.FRONTEND_URL and settings.FRONTEND_URL not in allowed_origins:
    allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notes.router)
app.include_router(favorites.router)
app.include_router(ai.router)


@app.get("/")
async def root():
    """ヘルスチェック"""
    return {"message": "Memoria API is running", "docs": "/docs", "version": "1.0.0"}
