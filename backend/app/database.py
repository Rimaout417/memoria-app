from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from databases import Database
from app.core.config import settings

# SQLAlchemy setup
engine = create_engine(
    settings.DATABASE_URL.replace("postgresql+psycopg", "postgresql")
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# metadata will be Base.metadata (includes all models)
metadata = Base.metadata

# Async database connection
database = Database(
    settings.DATABASE_URL.replace("postgresql+psycopg", "postgresql+asyncpg")
)
