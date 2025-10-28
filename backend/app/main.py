# FastAPI application entry point
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import notes
from app.schemas.note_schema import database, engine, metadata
import sys

metadata.create_all(engine)


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
{BLUE}🔍 OpenAPI JSON:{RESET} http://localhost:8000/openapi.json

{GREEN}{'='*60}{RESET}
"""
    print(message, file=sys.stderr)
    yield
    # Shutdown
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(notes.router, prefix="/notes", tags=["notes"])
