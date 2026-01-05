"""Modelo para cachear pontos de ônibus do OpenStreetMap."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index

from app.db.base import Base


class PontoOnibus(Base):
    """Ponto de ônibus cacheado do OpenStreetMap."""

    __tablename__ = "pontos_onibus"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(String(50), nullable=False, index=True)  # ID do OpenStreetMap
    nome = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    cidade = Column(String(100), nullable=False, index=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Índice composto para busca eficiente
    __table_args__ = (
        Index('idx_cidade_osm', 'cidade', 'osm_id'),
    )
