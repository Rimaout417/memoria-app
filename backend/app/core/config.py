# Application configuration
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # AI API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # AI Configuration
    AI_REQUEST_TIMEOUT: int = 30
    AI_MAX_RETRIES: int = 3
    AI_DEFAULT_PROVIDER: str = "openai"

    class ConfigDict:
        env_file = ".env"


settings = Settings()
