USE monitora;

INSERT INTO papel (descricao, ativo) VALUES
('ADMIN', true),
('Professor', true),
('Aluno', true);

INSERT INTO usuario (nome, email, senha, cpf, data_nascimento, telefone, especialidade, salario, ativo, fk_papel_id) VALUES
('Carlos Silva', 'carlos@monitora.com', '123456', '123.456.789-00', '1990-05-10', '41999990001', 'Gestão', 5000.00, true, 1),
('Ana Souza', 'ana@monitora.com', '123456', '987.654.321-00', '1985-08-20', '41999990002', 'Matemática', 7000.00, true, 2),
('João Pereira', 'joao@monitora.com', '123456', '111.222.333-44', '2003-03-15', '41999990003', NULL, NULL, true, 3),
('Mariana Lima', 'mariana@monitora.com', '123456', '555.666.777-88', '2002-11-25', '41999990004', NULL, NULL, true, 3);

INSERT INTO turma (id_curso, nome, codigo, periodo, ano, semestre, capacidade, turno, ativo) VALUES
(1, 'Sistemas de Informação - 1º Período', 'SI-2026-1', 1, 2026, 1, 40, 'NOITE', true),
(1, 'Sistemas de Informação - 2º Período', 'SI-2026-2', 2, 2026, 1, 40, 'NOITE', true);

INSERT INTO materia (nome, codigo, carga_horaria, descricao, ativo) VALUES
('Banco de Dados', 'BD101', 80, 'Introdução a banco de dados relacionais', true),
('Algoritmos', 'ALG101', 80, 'Lógica de programação', true),
('Estrutura de Dados', 'ED201', 80, 'Estruturas básicas', true);

INSERT INTO aviso (titulo, descricao, data_publicacao, ativo) VALUES
('Prova de BD', 'A prova será na próxima semana', NOW(), true),
('Trabalho de Algoritmos', 'Entrega até sexta-feira', NOW(), true);

INSERT INTO professor_materia (fk_usuario_id, fk_materia_id) VALUES
(2, 1),
(2, 2);

INSERT INTO usuario_turma (fk_usuario_id, fk_turma_id) VALUES
(3, 1),
(4, 1);

INSERT INTO materias_turma (fk_materia_id, fk_turma_id) VALUES
(1, 1),
(2, 1);

INSERT INTO materia_aviso (fk_materia_id, fk_aviso_id) VALUES
(1, 1),
(2, 2);

INSERT INTO nota (valor, observacao, data_lancamento, fk_materia_id, fk_usuario_id) VALUES
(8.5, 'Boa prova', NOW(), 1, 3),
(7.0, 'Precisa melhorar', NOW(), 2, 3),
(9.0, 'Excelente', NOW(), 1, 4);

INSERT INTO frequencia (data_aula, presente, justificativa, fk_usuario_id, fk_materia_id) VALUES
('2026-03-10', true, NULL, 3, 1),
('2026-03-10', false, 'Atestado médico', 4, 1),
('2026-03-11', true, NULL, 3, 2);