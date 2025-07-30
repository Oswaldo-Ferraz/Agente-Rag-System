# Configuração central da aplicação
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_NAME: str = os.getenv("DB_NAME", "chat_system_dev")
    DB_USER: str = os.getenv("DB_USER", "chat_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Chat System")
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "mock")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", 1536))

settings = Settings()
