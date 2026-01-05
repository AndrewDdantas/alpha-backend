from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.veiculo import Veiculo
from app.repositories.veiculo_repository import VeiculoRepository
from app.schemas.veiculo import VeiculoCreate, VeiculoUpdate, VeiculoList


class VeiculoService:
    """Serviço de negócios para Veículos."""

    def __init__(self, db: Session):
        self.repository = VeiculoRepository(db)

    def list_veiculos(self, skip: int = 0, limit: int = 100) -> VeiculoList:
        """Lista todos os veículos ativos."""
        veiculos = self.repository.get_all(skip=skip, limit=limit)
        total = self.repository.count()
        return VeiculoList(total=total, veiculos=veiculos)

    def get_veiculo(self, veiculo_id: int) -> Veiculo:
        """Busca um veículo por ID."""
        veiculo = self.repository.get_by_id(veiculo_id)
        if not veiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veículo não encontrado",
            )
        return veiculo

    def create_veiculo(self, veiculo_data: VeiculoCreate) -> Veiculo:
        """Cria um novo veículo."""
        # Verifica se placa já existe
        existing = self.repository.get_by_placa(veiculo_data.placa)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um veículo com esta placa",
            )
        return self.repository.create(veiculo_data)

    def update_veiculo(self, veiculo_id: int, veiculo_data: VeiculoUpdate) -> Veiculo:
        """Atualiza um veículo existente."""
        veiculo = self.get_veiculo(veiculo_id)

        # Se mudou a placa, verifica duplicidade
        if veiculo_data.placa and veiculo_data.placa != veiculo.placa:
            existing = self.repository.get_by_placa(veiculo_data.placa)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe um veículo com esta placa",
                )

        return self.repository.update(veiculo, veiculo_data)

    def delete_veiculo(self, veiculo_id: int) -> None:
        """Remove um veículo."""
        veiculo = self.get_veiculo(veiculo_id)
        self.repository.delete(veiculo)

    def get_capacidade_total(self) -> int:
        """Retorna a capacidade total da frota."""
        return self.repository.get_capacidade_total()

    def calcular_veiculos_necessarios(self, num_passageiros: int) -> dict:
        """
        Calcula quantos veículos são necessários para transportar X passageiros.
        Retorna sugestão de alocação.
        """
        veiculos = self.repository.get_all()
        if not veiculos:
            return {
                "passageiros": num_passageiros,
                "veiculos_disponiveis": 0,
                "capacidade_total": 0,
                "alocacao": [],
                "mensagem": "Nenhum veículo cadastrado",
            }

        # Ordena por capacidade (maior primeiro) para otimizar
        veiculos_ordenados = sorted(veiculos, key=lambda v: v.capacidade, reverse=True)

        alocacao = []
        passageiros_restantes = num_passageiros

        for veiculo in veiculos_ordenados:
            if passageiros_restantes <= 0:
                break

            passageiros_neste = min(veiculo.capacidade, passageiros_restantes)
            alocacao.append({
                "veiculo_id": veiculo.id,
                "placa": veiculo.placa,
                "modelo": veiculo.modelo,
                "capacidade": veiculo.capacidade,
                "passageiros_alocados": passageiros_neste,
                "motorista": veiculo.motorista,
            })
            passageiros_restantes -= passageiros_neste

        capacidade_total = sum(v.capacidade for v in veiculos)

        return {
            "passageiros": num_passageiros,
            "veiculos_disponiveis": len(veiculos),
            "veiculos_necessarios": len(alocacao),
            "capacidade_total": capacidade_total,
            "capacidade_restante": capacidade_total - num_passageiros if capacidade_total >= num_passageiros else 0,
            "alocacao": alocacao,
            "suficiente": passageiros_restantes <= 0,
            "faltam_vagas": passageiros_restantes if passageiros_restantes > 0 else 0,
        }
