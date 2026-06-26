from typing import List, Optional
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Configuracoes da aplicacao."""

    PROJECT_NAME: str = "Sistema de Gestao de Pessoas"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL_OVERRIDE: Optional[str] = Field(default=None, validation_alias="DATABASE_URL")
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "alpha"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

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
    SECRET_KEY: str = "change-me-in-local-env"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google Maps API
    GOOGLE_MAPS_API_KEY: str = ""

    # MinIO Storage (S3 Compatible)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minio_access_key"
    MINIO_SECRET_KEY: str = "minio_secret_key"
    MINIO_BUCKET: str = "sgp-presencas"
    MINIO_SECURE: bool = False
    MINIO_PUBLIC_URL: str = "http://localhost:9000"

    @property
    def DATABASE_URL(self) -> str:
        """Retorna DATABASE_URL explicita ou monta a URL com POSTGRES_*."""
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE

        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        host = self.POSTGRES_HOST
        port = self.POSTGRES_PORT
        database = quote_plus(self.POSTGRES_DB)
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
