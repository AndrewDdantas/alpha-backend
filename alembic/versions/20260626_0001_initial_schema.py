"""initial schema

Revision ID: 20260626_0001
Revises:
Create Date: 2026-06-26 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260626_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


tipo_pessoa_enum = sa.Enum("colaborador", "supervisor", "admin", name="tipopessoa")
status_diaria_enum = sa.Enum(
    "aberta",
    "fechada",
    "em_andamento",
    "concluida",
    "cancelada",
    name="statusdiaria",
)
status_inscricao_enum = sa.Enum(
    "pendente",
    "confirmada",
    "cancelada",
    "rejeitada",
    "concluida",
    "falta",
    name="statusinscricao",
)


def upgrade() -> None:
    op.create_table(
        "empresas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("cnpj", sa.String(length=18), nullable=False),
        sa.Column("razao_social", sa.String(length=200), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("telefone", sa.String(length=20), nullable=True),
        sa.Column("endereco", sa.String(length=255), nullable=True),
        sa.Column("cidade", sa.String(length=100), nullable=True),
        sa.Column("estado", sa.String(length=2), nullable=True),
        sa.Column("cep", sa.String(length=10), nullable=True),
        sa.Column("contato_nome", sa.String(length=100), nullable=True),
        sa.Column("contato_telefone", sa.String(length=20), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_empresas_cnpj"), "empresas", ["cnpj"], unique=True)
    op.create_index(op.f("ix_empresas_id"), "empresas", ["id"], unique=False)

    op.create_table(
        "permissoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.String(length=100), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("recurso", sa.String(length=50), nullable=False),
        sa.Column("acao", sa.String(length=50), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_permissoes_codigo"), "permissoes", ["codigo"], unique=True)
    op.create_index(op.f("ix_permissoes_id"), "permissoes", ["id"], unique=False)
    op.create_index(op.f("ix_permissoes_recurso"), "permissoes", ["recurso"], unique=False)

    op.create_table(
        "perfis",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column("sistema", sa.Boolean(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_perfis_codigo"), "perfis", ["codigo"], unique=True)
    op.create_index(op.f("ix_perfis_id"), "perfis", ["id"], unique=False)
    op.create_index(op.f("ix_perfis_nome"), "perfis", ["nome"], unique=True)

    op.create_table(
        "pontos_onibus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("osm_id", sa.String(length=50), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("cidade", sa.String(length=100), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_cidade_osm", "pontos_onibus", ["cidade", "osm_id"], unique=False)
    op.create_index(op.f("ix_pontos_onibus_cidade"), "pontos_onibus", ["cidade"], unique=False)
    op.create_index(op.f("ix_pontos_onibus_id"), "pontos_onibus", ["id"], unique=False)
    op.create_index(op.f("ix_pontos_onibus_osm_id"), "pontos_onibus", ["osm_id"], unique=False)

    op.create_table(
        "rotas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.String(length=255), nullable=True),
        sa.Column("horario_ida", sa.Time(), nullable=True),
        sa.Column("horario_volta", sa.Time(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rotas_id"), "rotas", ["id"], unique=False)

    op.create_table(
        "veiculos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("placa", sa.String(length=10), nullable=False),
        sa.Column("modelo", sa.String(length=100), nullable=False),
        sa.Column("capacidade", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=50), nullable=True),
        sa.Column("cor", sa.String(length=50), nullable=True),
        sa.Column("ano", sa.Integer(), nullable=True),
        sa.Column("motorista", sa.String(length=100), nullable=True),
        sa.Column("telefone_motorista", sa.String(length=20), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_veiculos_id"), "veiculos", ["id"], unique=False)
    op.create_index(op.f("ix_veiculos_placa"), "veiculos", ["placa"], unique=True)

    op.create_table(
        "perfil_permissao",
        sa.Column("perfil_id", sa.Integer(), nullable=False),
        sa.Column("permissao_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["perfil_id"], ["perfis.id"]),
        sa.ForeignKeyConstraint(["permissao_id"], ["permissoes.id"]),
        sa.PrimaryKeyConstraint("perfil_id", "permissao_id"),
    )

    op.create_table(
        "pontos_parada",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("endereco", sa.String(length=255), nullable=True),
        sa.Column("referencia", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("horario", sa.Time(), nullable=True),
        sa.Column("ordem", sa.Integer(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.Column("rota_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["rota_id"], ["rotas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pontos_parada_id"), "pontos_parada", ["id"], unique=False)

    op.create_table(
        "turnos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("hora_inicio", sa.Time(), nullable=False),
        sa.Column("hora_fim", sa.Time(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_turnos_id"), "turnos", ["id"], unique=False)

    op.create_table(
        "pessoas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("cpf", sa.String(length=14), nullable=False),
        sa.Column("pis", sa.String(length=14), nullable=False),
        sa.Column("telefone", sa.String(length=20), nullable=True),
        sa.Column("data_nascimento", sa.DateTime(), nullable=True),
        sa.Column("endereco", sa.String(length=255), nullable=True),
        sa.Column("complemento", sa.String(length=100), nullable=True),
        sa.Column("cidade", sa.String(length=100), nullable=True),
        sa.Column("estado", sa.String(length=2), nullable=True),
        sa.Column("cep", sa.String(length=10), nullable=True),
        sa.Column("senha_hash", sa.String(length=255), nullable=True),
        sa.Column("tipo_pessoa", tipo_pessoa_enum, nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=True),
        sa.Column("foto_url", sa.String(length=500), nullable=True),
        sa.Column("bloqueado", sa.Boolean(), nullable=True),
        sa.Column("motivo_bloqueio", sa.Text(), nullable=True),
        sa.Column("bloqueado_ate", sa.Date(), nullable=True),
        sa.Column("reset_token", sa.String(length=255), nullable=True),
        sa.Column("reset_token_expires", sa.DateTime(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.Column("ponto_parada_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["ponto_parada_id"], ["pontos_parada.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pessoas_cpf"), "pessoas", ["cpf"], unique=True)
    op.create_index(op.f("ix_pessoas_email"), "pessoas", ["email"], unique=True)
    op.create_index(op.f("ix_pessoas_id"), "pessoas", ["id"], unique=False)
    op.create_index(op.f("ix_pessoas_pis"), "pessoas", ["pis"], unique=True)
    op.create_index(op.f("ix_pessoas_reset_token"), "pessoas", ["reset_token"], unique=False)

    op.create_table(
        "pessoa_perfil",
        sa.Column("pessoa_id", sa.Integer(), nullable=False),
        sa.Column("perfil_id", sa.Integer(), nullable=False),
        sa.Column("atribuido_em", sa.DateTime(), nullable=True),
        sa.Column("atribuido_por_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["atribuido_por_id"], ["pessoas.id"]),
        sa.ForeignKeyConstraint(["perfil_id"], ["perfis.id"]),
        sa.ForeignKeyConstraint(["pessoa_id"], ["pessoas.id"]),
        sa.PrimaryKeyConstraint("pessoa_id", "perfil_id"),
    )

    op.create_table(
        "diarias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=150), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("horario_inicio", sa.Time(), nullable=True),
        sa.Column("horario_fim", sa.Time(), nullable=True),
        sa.Column("vagas", sa.Integer(), nullable=False),
        sa.Column("valor", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("local", sa.String(length=255), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("status", status_diaria_enum, nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("supervisor_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.ForeignKeyConstraint(["supervisor_id"], ["pessoas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_diarias_data"), "diarias", ["data"], unique=False)
    op.create_index(op.f("ix_diarias_id"), "diarias", ["id"], unique=False)

    op.create_table(
        "inscricoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("status", status_inscricao_enum, nullable=False),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.Column("pessoa_id", sa.Integer(), nullable=False),
        sa.Column("diaria_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["diaria_id"], ["diarias.id"]),
        sa.ForeignKeyConstraint(["pessoa_id"], ["pessoas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inscricoes_id"), "inscricoes", ["id"], unique=False)

    op.create_table(
        "alocacoes_diarias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("diaria_id", sa.Integer(), nullable=False),
        sa.Column("veiculo_id", sa.Integer(), nullable=False),
        sa.Column("rota_id", sa.Integer(), nullable=True),
        sa.Column("horario_saida", sa.Time(), nullable=True),
        sa.Column("observacao", sa.String(length=500), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["diaria_id"], ["diarias.id"]),
        sa.ForeignKeyConstraint(["rota_id"], ["rotas.id"]),
        sa.ForeignKeyConstraint(["veiculo_id"], ["veiculos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alocacoes_diarias_id"), "alocacoes_diarias", ["id"], unique=False)

    op.create_table(
        "registros_presenca",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("foto_url", sa.String(length=500), nullable=False),
        sa.Column("horario_registro", sa.DateTime(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("inscricao_id", sa.Integer(), nullable=False),
        sa.Column("registrado_por_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["inscricao_id"], ["inscricoes.id"]),
        sa.ForeignKeyConstraint(["registrado_por_id"], ["pessoas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_registros_presenca_id"), "registros_presenca", ["id"], unique=False)

    op.create_table(
        "alocacoes_colaboradores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("alocacao_diaria_id", sa.Integer(), nullable=False),
        sa.Column("inscricao_id", sa.Integer(), nullable=False),
        sa.Column("ponto_parada_id", sa.Integer(), nullable=True),
        sa.Column("horario_estimado", sa.Time(), nullable=True),
        sa.Column("ordem_embarque", sa.Integer(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["alocacao_diaria_id"], ["alocacoes_diarias.id"]),
        sa.ForeignKeyConstraint(["inscricao_id"], ["inscricoes.id"]),
        sa.ForeignKeyConstraint(["ponto_parada_id"], ["pontos_parada.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alocacoes_colaboradores_id"), "alocacoes_colaboradores", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_alocacoes_colaboradores_id"), table_name="alocacoes_colaboradores")
    op.drop_table("alocacoes_colaboradores")
    op.drop_index(op.f("ix_registros_presenca_id"), table_name="registros_presenca")
    op.drop_table("registros_presenca")
    op.drop_index(op.f("ix_alocacoes_diarias_id"), table_name="alocacoes_diarias")
    op.drop_table("alocacoes_diarias")
    op.drop_index(op.f("ix_inscricoes_id"), table_name="inscricoes")
    op.drop_table("inscricoes")
    op.drop_index(op.f("ix_diarias_id"), table_name="diarias")
    op.drop_index(op.f("ix_diarias_data"), table_name="diarias")
    op.drop_table("diarias")
    op.drop_table("pessoa_perfil")
    op.drop_index(op.f("ix_pessoas_reset_token"), table_name="pessoas")
    op.drop_index(op.f("ix_pessoas_pis"), table_name="pessoas")
    op.drop_index(op.f("ix_pessoas_id"), table_name="pessoas")
    op.drop_index(op.f("ix_pessoas_email"), table_name="pessoas")
    op.drop_index(op.f("ix_pessoas_cpf"), table_name="pessoas")
    op.drop_table("pessoas")
    op.drop_index(op.f("ix_turnos_id"), table_name="turnos")
    op.drop_table("turnos")
    op.drop_index(op.f("ix_pontos_parada_id"), table_name="pontos_parada")
    op.drop_table("pontos_parada")
    op.drop_table("perfil_permissao")
    op.drop_index(op.f("ix_veiculos_placa"), table_name="veiculos")
    op.drop_index(op.f("ix_veiculos_id"), table_name="veiculos")
    op.drop_table("veiculos")
    op.drop_index(op.f("ix_rotas_id"), table_name="rotas")
    op.drop_table("rotas")
    op.drop_index(op.f("ix_pontos_onibus_osm_id"), table_name="pontos_onibus")
    op.drop_index(op.f("ix_pontos_onibus_id"), table_name="pontos_onibus")
    op.drop_index(op.f("ix_pontos_onibus_cidade"), table_name="pontos_onibus")
    op.drop_index("idx_cidade_osm", table_name="pontos_onibus")
    op.drop_table("pontos_onibus")
    op.drop_index(op.f("ix_perfis_nome"), table_name="perfis")
    op.drop_index(op.f("ix_perfis_id"), table_name="perfis")
    op.drop_index(op.f("ix_perfis_codigo"), table_name="perfis")
    op.drop_table("perfis")
    op.drop_index(op.f("ix_permissoes_recurso"), table_name="permissoes")
    op.drop_index(op.f("ix_permissoes_id"), table_name="permissoes")
    op.drop_index(op.f("ix_permissoes_codigo"), table_name="permissoes")
    op.drop_table("permissoes")
    op.drop_index(op.f("ix_empresas_id"), table_name="empresas")
    op.drop_index(op.f("ix_empresas_cnpj"), table_name="empresas")
    op.drop_table("empresas")

    status_inscricao_enum.drop(op.get_bind(), checkfirst=True)
    status_diaria_enum.drop(op.get_bind(), checkfirst=True)
    tipo_pessoa_enum.drop(op.get_bind(), checkfirst=True)
