-- =============================================================================
-- SEED DATA - Alpha Transportes
-- Execute este script via pgAdmin após criar as tabelas
-- =============================================================================

-- Limpar dados existentes (ordem importa por causa das foreign keys)
TRUNCATE TABLE inscricoes CASCADE;
TRUNCATE TABLE diarias CASCADE;
TRUNCATE TABLE pessoas CASCADE;
TRUNCATE TABLE pontos_parada CASCADE;
TRUNCATE TABLE rotas CASCADE;
TRUNCATE TABLE veiculos CASCADE;
TRUNCATE TABLE turnos CASCADE;
TRUNCATE TABLE empresas CASCADE;

-- Reiniciar sequences
ALTER SEQUENCE empresas_id_seq RESTART WITH 1;
ALTER SEQUENCE turnos_id_seq RESTART WITH 1;
ALTER SEQUENCE veiculos_id_seq RESTART WITH 1;
ALTER SEQUENCE rotas_id_seq RESTART WITH 1;
ALTER SEQUENCE pontos_parada_id_seq RESTART WITH 1;
ALTER SEQUENCE pessoas_id_seq RESTART WITH 1;
ALTER SEQUENCE diarias_id_seq RESTART WITH 1;
ALTER SEQUENCE inscricoes_id_seq RESTART WITH 1;

-- =============================================================================
-- EMPRESA
-- =============================================================================
INSERT INTO empresas (nome, cnpj, razao_social, email, telefone, cidade, estado, contato_nome, ativo, criado_em, atualizado_em)
VALUES (
    'Alpha Transportes',
    '12345678000199',
    'Alpha Transportes LTDA',
    'contato@alpha.com.br',
    '(11) 99999-9999',
    'São Paulo',
    'SP',
    'Carlos Silva',
    true,
    NOW(),
    NOW()
);

-- =============================================================================
-- TURNOS
-- =============================================================================
INSERT INTO turnos (empresa_id, nome, hora_inicio, hora_fim, ativo, criado_em, atualizado_em) VALUES
(1, 'Manhã', '06:00:00', '14:00:00', true, NOW(), NOW()),
(1, 'Tarde', '14:00:00', '22:00:00', true, NOW(), NOW()),
(1, 'Noite', '22:00:00', '06:00:00', true, NOW(), NOW()),
(1, 'Comercial', '08:00:00', '18:00:00', true, NOW(), NOW()),
(1, 'Administrativo', '09:00:00', '17:00:00', true, NOW(), NOW());

-- =============================================================================
-- VEÍCULOS
-- =============================================================================
INSERT INTO veiculos (placa, modelo, cor, capacidade, motorista, telefone_motorista, ativo, criado_em, atualizado_em) VALUES
('ABC-1234', 'Mercedes Sprinter', 'Branca', 20, 'José Motorista', '(11) 98888-1111', true, NOW(), NOW()),
('DEF-5678', 'Volkswagen Volksbus', 'Prata', 30, 'Maria Motorista', '(11) 98888-2222', true, NOW(), NOW()),
('GHI-9012', 'Ford Transit', 'Cinza', 15, 'Pedro Motorista', '(11) 98888-3333', true, NOW(), NOW());

-- =============================================================================
-- ROTAS
-- =============================================================================
INSERT INTO rotas (nome, descricao, ativo, criado_em, atualizado_em) VALUES
('Rota Centro', 'Saindo do centro', true, NOW(), NOW()),
('Rota Zona Norte', 'Região norte', true, NOW(), NOW()),
('Rota Zona Sul', 'Região sul', true, NOW(), NOW()),
('Rota Zona Leste', 'Região leste', true, NOW(), NOW());

-- =============================================================================
-- PONTOS DE PARADA
-- =============================================================================
-- Rota Centro (id=1)
INSERT INTO pontos_parada (rota_id, nome, latitude, longitude, horario, ordem) VALUES
(1, 'Terminal Central', -23.5505, -46.6334, '06:30', 1),
(1, 'Shopping Centro', -23.5515, -46.6344, '06:45', 2),
(1, 'Praça da Sé', -23.5504, -46.6336, '07:00', 3);

-- Rota Zona Norte (id=2)
INSERT INTO pontos_parada (rota_id, nome, latitude, longitude, horario, ordem) VALUES
(2, 'Shopping Norte', -23.4905, -46.6234, '06:00', 1),
(2, 'Metrô Santana', -23.5005, -46.6134, '06:20', 2),
(2, 'Parque Norte', -23.5105, -46.6034, '06:40', 3);

-- Rota Zona Sul (id=3)
INSERT INTO pontos_parada (rota_id, nome, latitude, longitude, horario, ordem) VALUES
(3, 'Terminal Sul', -23.6505, -46.6534, '06:15', 1),
(3, 'Shopping Sul', -23.6305, -46.6434, '06:35', 2),
(3, 'Parque Ibirapuera', -23.5877, -46.6576, '06:55', 3);

-- Rota Zona Leste (id=4)
INSERT INTO pontos_parada (rota_id, nome, latitude, longitude, horario, ordem) VALUES
(4, 'Terminal Leste', -23.5405, -46.4734, '05:45', 1),
(4, 'Metrô Itaquera', -23.5405, -46.4534, '06:10', 2),
(4, 'Shopping Leste', -23.5405, -46.4334, '06:30', 3);

-- =============================================================================
-- PESSOAS
-- =============================================================================
-- Senha: admin123 (hash bcrypt)
-- Hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4W8Xw9X5a5a5a5a5a
-- NOTA: Você pode precisar gerar um novo hash. Use: python -c "from passlib.hash import bcrypt; print(bcrypt.hash('admin123'))"

-- Admin
INSERT INTO pessoas (nome, email, cpf, pis, telefone, senha_hash, tipo_pessoa, ativo, bloqueado, criado_em, atualizado_em)
VALUES (
    'Administrador',
    'admin@alpha.com.br',
    '00000000000',
    '00000000000',
    '(11) 99999-0000',
    '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y',
    'ADMIN',
    true,
    false,
    NOW(),
    NOW()
);

-- Funcionários (senha: 123456)
-- Hash para 123456: $2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y
INSERT INTO pessoas (nome, email, cpf, pis, telefone, senha_hash, tipo_pessoa, ativo, bloqueado, ponto_parada_id, criado_em, atualizado_em) VALUES
('Ana Silva', 'ana.silva@alpha.com.br', '10000000000', '20000000000', '(11) 97000-1000', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'SUPERVISOR', true, false, 1, NOW(), NOW()),
('Bruno Santos', 'bruno.santos@alpha.com.br', '10000000001', '20000000001', '(11) 97001-1001', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 2, NOW(), NOW()),
('Carla Oliveira', 'carla.oliveira@alpha.com.br', '10000000002', '20000000002', '(11) 97002-1002', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 3, NOW(), NOW()),
('Daniel Costa', 'daniel.costa@alpha.com.br', '10000000003', '20000000003', '(11) 97003-1003', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 4, NOW(), NOW()),
('Elena Ferreira', 'elena.ferreira@alpha.com.br', '10000000004', '20000000004', '(11) 97004-1004', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 5, NOW(), NOW()),
('Fernando Lima', 'fernando.lima@alpha.com.br', '10000000005', '20000000005', '(11) 97005-1005', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 6, NOW(), NOW()),
('Gabriela Souza', 'gabriela.souza@alpha.com.br', '10000000006', '20000000006', '(11) 97006-1006', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 7, NOW(), NOW()),
('Hugo Almeida', 'hugo.almeida@alpha.com.br', '10000000007', '20000000007', '(11) 97007-1007', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 8, NOW(), NOW()),
('Isabela Martins', 'isabela.martins@alpha.com.br', '10000000008', '20000000008', '(11) 97008-1008', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 9, NOW(), NOW()),
('João Pereira', 'joao.pereira@alpha.com.br', '10000000009', '20000000009', '(11) 97009-1009', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 10, NOW(), NOW()),
('Karen Ribeiro', 'karen.ribeiro@alpha.com.br', '10000000010', '20000000010', '(11) 97010-1010', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 11, NOW(), NOW()),
('Lucas Gomes', 'lucas.gomes@alpha.com.br', '10000000011', '20000000011', '(11) 97011-1011', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 12, NOW(), NOW()),
('Marina Rocha', 'marina.rocha@alpha.com.br', '10000000012', '20000000012', '(11) 97012-1012', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 1, NOW(), NOW()),
('Nelson Dias', 'nelson.dias@alpha.com.br', '10000000013', '20000000013', '(11) 97013-1013', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 2, NOW(), NOW()),
('Olívia Fernandes', 'olivia.fernandes@alpha.com.br', '10000000014', '20000000014', '(11) 97014-1014', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 3, NOW(), NOW()),
('Paulo Cardoso', 'paulo.cardoso@alpha.com.br', '10000000015', '20000000015', '(11) 97015-1015', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 4, NOW(), NOW()),
('Queila Barbosa', 'queila.barbosa@alpha.com.br', '10000000016', '20000000016', '(11) 97016-1016', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 5, NOW(), NOW()),
('Ricardo Moreira', 'ricardo.moreira@alpha.com.br', '10000000017', '20000000017', '(11) 97017-1017', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 6, NOW(), NOW()),
('Sandra Nascimento', 'sandra.nascimento@alpha.com.br', '10000000018', '20000000018', '(11) 97018-1018', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 7, NOW(), NOW()),
('Thiago Araújo', 'thiago.araujo@alpha.com.br', '10000000019', '20000000019', '(11) 97019-1019', '$2b$12$Ukp.gYtAIsFAnxZ3y6Eo8.dkuGW9dLP5Z6TUwRgTjWbt/.bLC5t5y', 'COLABORADOR', true, false, 8, NOW(), NOW());

-- =============================================================================
-- DIÁRIAS
-- =============================================================================
-- Diária para hoje (FECHADA - permite registro de presença)
INSERT INTO diarias (titulo, descricao, data, horario_inicio, horario_fim, vagas, valor, local, empresa_id, supervisor_id, status, criado_em, atualizado_em)
VALUES (
    'Manutenção Industrial - Turno Manhã',
    'Serviço de manutenção preventiva',
    CURRENT_DATE,
    '06:00:00',
    '14:00:00',
    20,
    150.00,
    'Fábrica São Paulo - Zona Leste',
    1,
    2, -- Ana Silva é supervisora
    'FECHADA',
    NOW(),
    NOW()
);

-- Diária para amanhã (ABERTA)
INSERT INTO diarias (titulo, descricao, data, horario_inicio, horario_fim, vagas, valor, local, empresa_id, status, criado_em, atualizado_em)
VALUES (
    'Montagem de Equipamentos - Turno Tarde',
    'Montagem de linha de produção',
    CURRENT_DATE + INTERVAL '1 day',
    '14:00:00',
    '22:00:00',
    15,
    180.00,
    'Centro de Distribuição - Guarulhos',
    1,
    'ABERTA',
    NOW(),
    NOW()
);

-- =============================================================================
-- INSCRIÇÕES (10 funcionários na diária de hoje)
-- =============================================================================
INSERT INTO inscricoes (diaria_id, pessoa_id, status, criado_em, atualizado_em) VALUES
(1, 2, 'CONFIRMADA', NOW(), NOW()),   -- Ana Silva
(1, 3, 'CONFIRMADA', NOW(), NOW()),   -- Bruno Santos
(1, 4, 'CONFIRMADA', NOW(), NOW()),   -- Carla Oliveira
(1, 5, 'CONFIRMADA', NOW(), NOW()),   -- Daniel Costa
(1, 6, 'CONFIRMADA', NOW(), NOW()),   -- Elena Ferreira
(1, 7, 'CONFIRMADA', NOW(), NOW()),   -- Fernando Lima
(1, 8, 'CONFIRMADA', NOW(), NOW()),   -- Gabriela Souza
(1, 9, 'CONFIRMADA', NOW(), NOW()),   -- Hugo Almeida
(1, 10, 'CONFIRMADA', NOW(), NOW()),  -- Isabela Martins
(1, 11, 'CONFIRMADA', NOW(), NOW());  -- João Pereira

-- =============================================================================
-- RESUMO
-- =============================================================================
-- ✅ 1 Empresa: Alpha Transportes
-- ✅ 5 Turnos
-- ✅ 3 Veículos
-- ✅ 4 Rotas com 12 pontos de parada
-- ✅ 1 Admin: admin@alpha.com.br / admin123
-- ✅ 20 Funcionários (senha: 123456)
-- ✅ 2 Diárias (hoje e amanhã)
-- ✅ 10 Inscrições na diária de hoje
--
-- Para testar presença:
--   Login: ana.silva@alpha.com.br / 123456 (SUPERVISOR)
--   Ela é supervisora da diária de hoje
