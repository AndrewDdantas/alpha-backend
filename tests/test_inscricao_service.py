from datetime import date, time, timedelta
from typing import Optional

import pytest
from fastapi import HTTPException

from app.models.diaria import Diaria, Inscricao
from app.models.empresa import Empresa
from app.models.enums import StatusDiaria, StatusInscricao, TipoPessoa
from app.models.pessoa import Pessoa
from app.schemas.diaria import InscricaoCreate
from app.services.diaria_service import InscricaoService


def create_empresa(db_session) -> Empresa:
    empresa = Empresa(nome="Empresa Teste", cnpj="00.000.000/0001-00")
    db_session.add(empresa)
    db_session.commit()
    db_session.refresh(empresa)
    return empresa


def create_pessoa(db_session, *, bloqueado: bool = False, bloqueado_ate=None) -> Pessoa:
    pessoa = Pessoa(
        nome="Pessoa Teste",
        email="pessoa@example.com",
        cpf="000.000.000-00",
        pis="12345678901",
        tipo_pessoa=TipoPessoa.COLABORADOR,
        bloqueado=bloqueado,
        bloqueado_ate=bloqueado_ate,
    )
    db_session.add(pessoa)
    db_session.commit()
    db_session.refresh(pessoa)
    return pessoa


def create_diaria(
    db_session,
    empresa: Empresa,
    *,
    data: Optional[date] = None,
    horario_inicio: Optional[time] = time(8, 0),
    horario_fim: Optional[time] = time(17, 0),
    vagas: int = 1,
    status: StatusDiaria = StatusDiaria.ABERTA,
) -> Diaria:
    diaria = Diaria(
        titulo="Diaria Teste",
        data=data or date.today() + timedelta(days=1),
        horario_inicio=horario_inicio,
        horario_fim=horario_fim,
        vagas=vagas,
        status=status,
        empresa_id=empresa.id,
    )
    db_session.add(diaria)
    db_session.commit()
    db_session.refresh(diaria)
    return diaria


def create_inscricao(
    db_session,
    pessoa: Pessoa,
    diaria: Diaria,
    *,
    status: StatusInscricao = StatusInscricao.PENDENTE,
) -> Inscricao:
    inscricao = Inscricao(pessoa_id=pessoa.id, diaria_id=diaria.id, status=status)
    db_session.add(inscricao)
    db_session.commit()
    db_session.refresh(inscricao)
    return inscricao


def assert_http_error(exc_info, status_code: int, detail_part: str) -> None:
    assert exc_info.value.status_code == status_code
    assert detail_part in exc_info.value.detail


def test_inscrever_rejeita_diaria_inexistente(db_session):
    pessoa = create_pessoa(db_session)
    service = InscricaoService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        service.inscrever(pessoa.id, InscricaoCreate(diaria_id=999))

    assert_http_error(exc_info, 404, "encontrada")


def test_inscrever_rejeita_diaria_nao_aberta(db_session):
    empresa = create_empresa(db_session)
    pessoa = create_pessoa(db_session)
    diaria = create_diaria(db_session, empresa, status=StatusDiaria.FECHADA)
    service = InscricaoService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        service.inscrever(pessoa.id, InscricaoCreate(diaria_id=diaria.id))

    assert_http_error(exc_info, 400, "aberta")


def test_inscrever_rejeita_pessoa_bloqueada(db_session):
    empresa = create_empresa(db_session)
    pessoa = create_pessoa(
        db_session,
        bloqueado=True,
        bloqueado_ate=date.today() + timedelta(days=2),
    )
    diaria = create_diaria(db_session, empresa)
    service = InscricaoService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        service.inscrever(pessoa.id, InscricaoCreate(diaria_id=diaria.id))

    assert_http_error(exc_info, 403, "bloqueada")


def test_inscrever_rejeita_inscricao_duplicada_ativa(db_session):
    empresa = create_empresa(db_session)
    pessoa = create_pessoa(db_session)
    diaria = create_diaria(db_session, empresa, vagas=2)
    create_inscricao(db_session, pessoa, diaria, status=StatusInscricao.PENDENTE)
    service = InscricaoService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        service.inscrever(pessoa.id, InscricaoCreate(diaria_id=diaria.id))

    assert_http_error(exc_info, 400, "inscrito")


def test_inscrever_rejeita_diaria_sem_vagas(db_session):
    empresa = create_empresa(db_session)
    pessoa = create_pessoa(db_session)
    outra_pessoa = Pessoa(
        nome="Outra Pessoa",
        email="outra@example.com",
        cpf="111.111.111-11",
        pis="10987654321",
        tipo_pessoa=TipoPessoa.COLABORADOR,
    )
    db_session.add(outra_pessoa)
    db_session.commit()
    db_session.refresh(outra_pessoa)

    diaria = create_diaria(db_session, empresa, vagas=1)
    create_inscricao(db_session, outra_pessoa, diaria, status=StatusInscricao.CONFIRMADA)
    service = InscricaoService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        service.inscrever(pessoa.id, InscricaoCreate(diaria_id=diaria.id))

    assert_http_error(exc_info, 400, "vagas")


def test_inscrever_rejeita_conflito_de_horario(db_session):
    empresa = create_empresa(db_session)
    pessoa = create_pessoa(db_session)
    amanha = date.today() + timedelta(days=1)
    diaria_existente = create_diaria(
        db_session,
        empresa,
        data=amanha,
        horario_inicio=time(8, 0),
        horario_fim=time(17, 0),
    )
    nova_diaria = create_diaria(
        db_session,
        empresa,
        data=amanha,
        horario_inicio=time(16, 0),
        horario_fim=time(20, 0),
    )
    create_inscricao(db_session, pessoa, diaria_existente, status=StatusInscricao.CONFIRMADA)
    service = InscricaoService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        service.inscrever(pessoa.id, InscricaoCreate(diaria_id=nova_diaria.id))

    assert_http_error(exc_info, 400, "conflita")


def test_inscrever_cria_inscricao_quando_regras_validas(db_session):
    empresa = create_empresa(db_session)
    pessoa = create_pessoa(db_session)
    diaria = create_diaria(db_session, empresa, vagas=1)
    service = InscricaoService(db_session)

    inscricao = service.inscrever(pessoa.id, InscricaoCreate(diaria_id=diaria.id))

    assert inscricao.id is not None
    assert inscricao.pessoa_id == pessoa.id
    assert inscricao.diaria_id == diaria.id
    assert inscricao.status == StatusInscricao.PENDENTE
