from enum import Enum


class TipoPessoa(str, Enum):
    """Tipos de pessoa no sistema."""

    COLABORADOR = "colaborador"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


class StatusDiaria(str, Enum):
    """Status da diária."""

    ABERTA = "aberta"           # Diária aberta para inscrições
    FECHADA = "fechada"         # Inscrições encerradas
    EM_ANDAMENTO = "em_andamento"  # Diária acontecendo
    CONCLUIDA = "concluida"     # Diária finalizada
    CANCELADA = "cancelada"     # Diária cancelada


class StatusInscricao(str, Enum):
    """Status da inscrição do colaborador."""

    PENDENTE = "pendente"       # Aguardando confirmação
    CONFIRMADA = "confirmada"   # Inscrição confirmada
    CANCELADA = "cancelada"     # Inscrição cancelada pelo colaborador
    REJEITADA = "rejeitada"     # Inscrição rejeitada pelo admin
    CONCLUIDA = "concluida"     # Colaborador completou a diária
    FALTA = "falta"             # Falta - sem presença confirmada

