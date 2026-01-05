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
        "https://andrewddantas.github.io",  # GitHub Pages
        "https://andrewddantas.github.io/alpha-frontend"
    ]

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google Maps API
    GOOGLE_MAPS_API_KEY: str = "AIzaSyA758ldyTDqtomDirS2I-gtyvtv5_wVLkI"

    # Supabase Storage (S3)
    SUPABASE_STORAGE_URL: str = "https://pdwrzddksthiewwqpfml.storage.supabase.co/storage/v1/s3"
    SUPABASE_STORAGE_ACCESS_KEY: str = "c7328c01c8bf99cc3c42fd3867dd233a"
    SUPABASE_STORAGE_SECRET_KEY: str = "bf87cbbe208fa7f5af33430cdfbc39f8053afa8d02c65ac32919e4b299b4bc89"
    SUPABASE_STORAGE_BUCKET: str = "ALPHA"
    SUPABASE_PROJECT_URL: str = "https://pdwrzddksthiewwqpfml.supabase.co"
    SUPABASE_STORAGE_REGION: str = "us-west-2"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignora variáveis extras no .env


settings = Settings()

