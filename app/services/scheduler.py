"""
Scheduler para tarefas automáticas do sistema.
Inclui fechamento automático de diárias antes do início.
"""
import threading
import time as time_module
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.diaria import Diaria
from app.models.enums import StatusDiaria


def fechar_diarias_proximas(db: Session, horas_antes: int = 4) -> List[int]:
    """
    Fecha diárias que estão próximas de começar.

    Args:
        db: Sessão do banco de dados
        horas_antes: Quantas horas antes do início fechar a diária

    Returns:
        Lista de IDs das diárias fechadas
    """
    agora = datetime.utcnow()
    limite = agora + timedelta(hours=horas_antes)

    # Busca diárias abertas que começam em menos de X horas
    diarias = (
        db.query(Diaria)
        .filter(Diaria.status == StatusDiaria.ABERTA)
        .filter(Diaria.data <= limite.date())
        .all()
    )

    fechadas = []
    for diaria in diarias:
        # Combina data + horário de início
        if diaria.horario_inicio:
            inicio = datetime.combine(diaria.data, diaria.horario_inicio)
        else:
            # Se não tem horário, considera meia-noite
            inicio = datetime.combine(diaria.data, datetime.min.time())

        # Verifica se está dentro do limite
        if inicio <= limite:
            diaria.status = StatusDiaria.FECHADA
            fechadas.append(diaria.id)
            print(f"[Scheduler] Diária #{diaria.id} '{diaria.titulo}' fechada automaticamente")

    if fechadas:
        db.commit()

    return fechadas


def executar_scheduler():
    """
    Loop principal do scheduler.
    Roda a cada 30 minutos verificando diárias para fechar.
    Roda a cada hora verificando faltas.
    """
    print("[Scheduler] Iniciando scheduler de diárias...")
    contador_ciclos = 0

    while True:
        try:
            db = SessionLocal()
            
            # Fecha diárias próximas (a cada 30 min)
            fechadas = fechar_diarias_proximas(db, horas_antes=4)
            if fechadas:
                print(f"[Scheduler] {len(fechadas)} diária(s) fechada(s) automaticamente")
            
            # Marca faltas (a cada hora - ciclos pares)
            if contador_ciclos % 2 == 0:
                from app.services.attendance_service import AttendanceService
                attendance_service = AttendanceService(db)
                resultado = attendance_service.marcar_faltas_automaticas()
                if resultado['total_faltas'] > 0:
                    print(f"[Scheduler] {resultado['total_faltas']} falta(s) marcada(s), {resultado['total_penalidades']} penalidade(s) aplicada(s)")
            
            db.close()
        except Exception as e:
            print(f"[Scheduler] Erro: {e}")

        contador_ciclos += 1
        # Aguarda 30 minutos
        time_module.sleep(30 * 60)


def iniciar_scheduler_em_background():
    """Inicia o scheduler em uma thread separada."""
    thread = threading.Thread(target=executar_scheduler, daemon=True)
    thread.start()
    print("[Scheduler] Thread iniciada em background")
