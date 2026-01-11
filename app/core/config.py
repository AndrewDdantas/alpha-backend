from typing import List

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    """Configurações da aplicação."""

    PROJECT_NAME: str = "Sistema de Gestão de Pessoas"
    API_V1_STR: str = "/api/v1"

    # Supabase Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/postgres"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://andrewddantas.github.io",
    ]

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google Maps API
    GOOGLE_MAPS_API_KEY: str = "AIzaSyA758ldyTDqtomDirS2I-gtyvtv5_wVLkI"

    # MinIO Storage (S3 Compatible)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minio_admin"
    MINIO_SECRET_KEY: str = "minio_secret"
    MINIO_BUCKET: str = "sgp-presencas"
    MINIO_SECURE: bool = False  # True se usar HTTPS
    MINIO_PUBLIC_URL: str = "http://localhost:9000"  # URL pública para acessar arquivos

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignora variáveis extras no .env


settings = Settings()

