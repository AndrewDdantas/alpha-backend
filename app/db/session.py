from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verifica conexões antes de usar
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
