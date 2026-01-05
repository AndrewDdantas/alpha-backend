"""
Serviço para buscar pontos de ônibus via Overpass API (OpenStreetMap).
"""
import overpy
import time
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models.ponto_onibus import PontoOnibus


class OverpassService:
    """Serviço para consultar Overpass API e gerenciar cache de pontos."""

    # Servidores Overpass alternativos
    SERVERS = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    ]

    def __init__(self, db: Session):
        self.db = db

    def buscar_pontos_cidade(self, cidade: str, force_refresh: bool = False) -> List[Dict]:
        """
        Busca pontos de ônibus de uma cidade.
        Primeiro verifica o cache, se não existir, consulta Overpass API.
        
        Args:
            cidade: Nome da cidade (ex: "Jundiaí")
            force_refresh: Se True, ignora cache e busca novamente
            
        Returns:
            Lista de dicts com dados dos pontos
        """
        # Normaliza nome da cidade
        cidade_normalizada = cidade.strip().title()
        
        # Verifica cache
        if not force_refresh:
            pontos_cache = self.db.query(PontoOnibus).filter(
                PontoOnibus.cidade == cidade_normalizada
            ).all()
            
            if pontos_cache:
                return [self._ponto_to_dict(p) for p in pontos_cache]
        
        # Se não tem cache ou force_refresh, busca na API
        pontos_api = self._buscar_overpass(cidade_normalizada)
        
        if pontos_api:
            # Limpa cache anterior se force_refresh
            if force_refresh:
                self.db.query(PontoOnibus).filter(
                    PontoOnibus.cidade == cidade_normalizada
                ).delete()
            
            # Salva no cache
            for ponto in pontos_api:
                ponto_db = PontoOnibus(
                    osm_id=ponto["osm_id"],
                    nome=ponto.get("nome"),
                    latitude=ponto["latitude"],
                    longitude=ponto["longitude"],
                    cidade=cidade_normalizada,
                )
                self.db.add(ponto_db)
            
            self.db.commit()
        
        return pontos_api

    def _buscar_overpass(self, cidade: str, max_retries: int = 2) -> List[Dict]:
        """Consulta Overpass API com fallback de servidores."""
        
        query = f"""
        [out:json][timeout:120];
        area["name"="{cidade}"]->.searchArea;
        (
          node["highway"="bus_stop"](area.searchArea);
          node["amenity"="bus_station"](area.searchArea);
        );
        out body;
        """

        for attempt in range(max_retries):
            for server in self.SERVERS:
                try:
                    api = overpy.Overpass(url=server)
                    result = api.query(query)
                    
                    pontos = []
                    for node in result.nodes:
                        pontos.append({
                            "osm_id": str(node.id),
                            "nome": node.tags.get("name"),
                            "latitude": float(node.lat),
                            "longitude": float(node.lon),
                            "cidade": cidade,
                        })
                    
                    return pontos
                    
                except Exception as e:
                    print(f"Overpass error ({server}): {e}")
                    time.sleep(1)
            
            if attempt < max_retries - 1:
                time.sleep(3)
        
        return []

    def _ponto_to_dict(self, ponto: PontoOnibus) -> Dict:
        """Converte modelo para dict."""
        return {
            "id": ponto.id,
            "osm_id": ponto.osm_id,
            "nome": ponto.nome,
            "latitude": ponto.latitude,
            "longitude": ponto.longitude,
            "cidade": ponto.cidade,
        }


def get_overpass_service(db: Session) -> OverpassService:
    """Factory function para criar OverpassService."""
    return OverpassService(db)
