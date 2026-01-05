"""
Serviço de integração com Google Maps API.
Calcula tempos de viagem e distâncias entre pontos.
"""
import httpx
from typing import List, Dict, Optional, Tuple

from app.core.config import settings


class GoogleMapsService:
    """Serviço para integração com Google Maps Directions API."""

    BASE_URL = "https://maps.googleapis.com/maps/api/directions/json"

    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY

    async def get_route_directions(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        waypoints: Optional[List[Tuple[float, float]]] = None,
    ) -> Dict:
        """
        Obtém direções de rota usando Google Directions API.

        Args:
            origin: Tupla (latitude, longitude) do ponto de origem
            destination: Tupla (latitude, longitude) do ponto de destino
            waypoints: Lista opcional de pontos intermediários

        Returns:
            Dados da rota incluindo distância, duração e passos
        """
        params = {
            "origin": f"{origin[0]},{origin[1]}",
            "destination": f"{destination[0]},{destination[1]}",
            "key": self.api_key,
            "language": "pt-BR",
            "mode": "driving",
        }

        if waypoints:
            waypoints_str = "|".join([f"{lat},{lng}" for lat, lng in waypoints])
            params["waypoints"] = f"optimize:true|{waypoints_str}"

        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, params=params)
            data = response.json()

        if data.get("status") != "OK":
            return {
                "success": False,
                "error": data.get("status"),
                "message": data.get("error_message", "Erro ao obter direções"),
            }

        route = data["routes"][0]
        legs = route["legs"]

        # Calcula totais
        total_distance = sum(leg["distance"]["value"] for leg in legs)  # metros
        total_duration = sum(leg["duration"]["value"] for leg in legs)  # segundos

        # Monta informações de cada trecho
        trechos = []
        for i, leg in enumerate(legs):
            trechos.append({
                "origem": leg["start_address"],
                "destino": leg["end_address"],
                "distancia_metros": leg["distance"]["value"],
                "distancia_texto": leg["distance"]["text"],
                "duracao_segundos": leg["duration"]["value"],
                "duracao_texto": leg["duration"]["text"],
            })

        return {
            "success": True,
            "distancia_total_metros": total_distance,
            "distancia_total_km": round(total_distance / 1000, 2),
            "duracao_total_segundos": total_duration,
            "duracao_total_minutos": round(total_duration / 60, 1),
            "trechos": trechos,
            "polyline": route.get("overview_polyline", {}).get("points"),
        }

    async def calculate_stop_times(
        self,
        pontos: List[Dict],
        horario_partida: str,
    ) -> List[Dict]:
        """
        Calcula os horários estimados de passagem em cada ponto.

        Args:
            pontos: Lista de pontos com latitude/longitude ordenados
            horario_partida: Horário de partida do primeiro ponto (HH:MM)

        Returns:
            Lista de pontos com horários estimados de passagem
        """
        if len(pontos) < 2:
            return pontos

        # Converte horário inicial para minutos
        horas, minutos = map(int, horario_partida.split(":"))
        tempo_atual = horas * 60 + minutos

        resultado = []

        for i, ponto in enumerate(pontos):
            ponto_com_horario = {**ponto}

            if i == 0:
                # Primeiro ponto: horário de partida
                ponto_com_horario["horario_estimado"] = horario_partida
            else:
                # Calcula tempo do ponto anterior até este
                ponto_anterior = pontos[i - 1]

                if (
                    ponto_anterior.get("latitude")
                    and ponto_anterior.get("longitude")
                    and ponto.get("latitude")
                    and ponto.get("longitude")
                ):
                    # Usa API para calcular tempo real
                    directions = await self.get_route_directions(
                        origin=(ponto_anterior["latitude"], ponto_anterior["longitude"]),
                        destination=(ponto["latitude"], ponto["longitude"]),
                    )

                    if directions.get("success"):
                        tempo_atual += directions["duracao_total_minutos"]
                    else:
                        # Estimativa padrão de 5 minutos entre pontos
                        tempo_atual += 5
                else:
                    # Sem coordenadas, usa estimativa
                    tempo_atual += 5

                # Converte minutos de volta para HH:MM
                horas_est = int(tempo_atual // 60) % 24
                minutos_est = int(tempo_atual % 60)
                ponto_com_horario["horario_estimado"] = f"{horas_est:02d}:{minutos_est:02d}"

            resultado.append(ponto_com_horario)

        return resultado


# Instância singleton
google_maps_service = GoogleMapsService()
