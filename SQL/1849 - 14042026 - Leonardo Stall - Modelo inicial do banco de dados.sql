-- ESSA AÇÃO APAGARÁ TODOS OS DADOS DO BANCO DE DADOS
DROP DATABASE IF EXISTS monitora;

CREATE DATABASE monitora;

USE monitora;

-- PAPEL
CREATE TABLE papel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(255),
    ativo BOOLEAN,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
	data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- USUARIO
CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    senha VARCHAR(255),
    cpf VARCHAR(14) UNIQUE,
    data_nascimento DATE,
    telefone VARCHAR(20),
    especialidade VARCHAR(255),
    salario DECIMAL(10,2),
    ativo BOOLEAN,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
	data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    fk_papel_id INT,
    
    CONSTRAINT FK_usuario_papel
    FOREIGN KEY (fk_papel_id)
    REFERENCES papel(id)
    ON DELETE CASCADE
);

-- TURMA
CREATE TABLE turma (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_curso INT,
    nome VARCHAR(255),
    codigo VARCHAR(50) UNIQUE,
    periodo INT,
    ano INT,
    semestre INT,
    capacidade INT,
    turno VARCHAR(20),
    ativo BOOLEAN,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
	data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- MATERIA
CREATE TABLE materia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    codigo VARCHAR(50) UNIQUE,
    carga_horaria INT,
    descricao VARCHAR(500),
    ativo BOOLEAN,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
	data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- AVISO
CREATE TABLE aviso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255),
    descricao VARCHAR(1000),
    data_publicacao DATETIME,
    ativo BOOLEAN,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
	data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- NOTA
CREATE TABLE nota (
    id INT AUTO_INCREMENT PRIMARY KEY,
    valor DECIMAL(5,2),
    observacao VARCHAR(255),
    data_lancamento DATETIME,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
	data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    fk_materia_id INT,
    fk_usuario_id INT,

        FOREIGN KEY (fk_materia_id)
        REFERENCES materia(id)
        ON DELETE CASCADE,

        FOREIGN KEY (fk_usuario_id)
        REFERENCES usuario(id)
        ON DELETE CASCADE
    );

-- FREQUENCIA
CREATE TABLE frequencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_aula DATE,
    presente BOOLEAN,
    justificativa VARCHAR(255),
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
	data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    fk_usuario_id INT,
    fk_materia_id INT,

    FOREIGN KEY (fk_usuario_id)
    REFERENCES usuario(id)
    ON DELETE CASCADE,

    FOREIGN KEY (fk_materia_id)
    REFERENCES materia(id)
    ON DELETE CASCADE
);

-- TABELAS N:N

CREATE TABLE usuario_turma (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fk_usuario_id INT,
    fk_turma_id INT,

    UNIQUE (fk_usuario_id, fk_turma_id),

    FOREIGN KEY (fk_usuario_id)
    REFERENCES usuario(id)
    ON DELETE CASCADE,

    FOREIGN KEY (fk_turma_id)
    REFERENCES turma(id)
    ON DELETE CASCADE
);

CREATE TABLE materia_aviso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fk_materia_id INT,
    fk_aviso_id INT,

    UNIQUE (fk_materia_id, fk_aviso_id),

    FOREIGN KEY (fk_materia_id)
    REFERENCES materia(id)
    ON DELETE CASCADE,

    FOREIGN KEY (fk_aviso_id)
    REFERENCES aviso(id)
    ON DELETE CASCADE
);

CREATE TABLE materias_turma (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fk_materia_id INT,
    fk_turma_id INT,

    UNIQUE (fk_materia_id, fk_turma_id),

    FOREIGN KEY (fk_materia_id)
    REFERENCES materia(id)
    ON DELETE CASCADE,

    FOREIGN KEY (fk_turma_id)
    REFERENCES turma(id)
    ON DELETE CASCADE
);

CREATE TABLE professor_materia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fk_usuario_id INT,
    fk_materia_id INT,

    UNIQUE (fk_usuario_id, fk_materia_id),

    FOREIGN KEY (fk_usuario_id)
    REFERENCES usuario(id)
    ON DELETE CASCADE,

    FOREIGN KEY (fk_materia_id)
    REFERENCES materia(id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS professor_turma_materia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fk_usuario_id INT NOT NULL,
    fk_turma_id INT NOT NULL,
    fk_materia_id INT NOT NULL,

    UNIQUE (fk_usuario_id, fk_turma_id, fk_materia_id),

    FOREIGN KEY (fk_usuario_id)
    REFERENCES usuario(id)
    ON DELETE CASCADE,

    FOREIGN KEY (fk_turma_id)
    REFERENCES turma(id)
    ON DELETE CASCADE,

    FOREIGN KEY (fk_materia_id)
    REFERENCES materia(id)
    ON DELETE CASCADE
);


USE monitora;

-- 1. Cria a tabela evento_calendario se ainda não existir (caso seja instalação nova)
CREATE TABLE IF NOT EXISTS evento_calendario (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    titulo          VARCHAR(255) NOT NULL,
    descricao       VARCHAR(1000),
    data_inicio     DATETIME NOT NULL,
    data_fim        DATETIME,
    cor             VARCHAR(20) DEFAULT '#4caebe',
    tipo            VARCHAR(30) DEFAULT 'evento',
    ativo           BOOLEAN DEFAULT TRUE,
    data_criacao    DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    fk_criador_id   INT NOT NULL,
    fk_turma_id     INT,
    fk_materia_id   INT,

    FOREIGN KEY (fk_criador_id) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (fk_turma_id)   REFERENCES turma(id)   ON DELETE SET NULL,
    FOREIGN KEY (fk_materia_id) REFERENCES materia(id) ON DELETE SET NULL
);

-- 2. Adiciona coluna de visibilidade (para eventos do coordenador):
--    'todos'       = alunos + professores enxergam
--    'alunos'      = apenas alunos da turma vinculada
--    'professores' = apenas professores
-- Padrão 'todos' garante compatibilidade com eventos já existentes.
ALTER TABLE evento_calendario
    ADD COLUMN visibilidade ENUM('todos','alunos','professores') NOT NULL DEFAULT 'todos';

-- 3. Adiciona flag de evento pessoal (criado pelo usuário para si mesmo).
--    TRUE  = só o próprio criador enxerga
--    FALSE = visível conforme regras de turma/visibilidade
ALTER TABLE evento_calendario
    ADD COLUMN pessoal BOOLEAN NOT NULL DEFAULT FALSE;


-- ================================================================
-- Sistema de Mensagens do Monitora+
-- ================================================================

USE monitora;

-- ── 1. Remove estrutura antiga (se existir) ──────────────────────
DROP TABLE IF EXISTS aviso_destinatario;
DROP TABLE IF EXISTS aviso;

-- ── 2. Tabela principal de mensagens ────────────────────────────────
-- Cada mensagem tem um remetente (fk_remetente_id) e pode ter como
-- destino uma combinação de: turma inteira, matéria específica,
-- papel (aluno/professor/coordenador) ou usuário individual.
CREATE TABLE mensagem (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    titulo              VARCHAR(255)  NOT NULL,
    descricao           TEXT          NOT NULL,
    data_publicacao     DATETIME      DEFAULT CURRENT_TIMESTAMP,
    ativo               BOOLEAN       DEFAULT TRUE,

    -- Quem enviou
    fk_remetente_id     INT           NOT NULL,

    -- Escopo do envio (todos opcionais; combinados pelo backend)
    -- NULL = sem restrição naquele nível
    fk_turma_id         INT           NULL,      -- turma alvo (NULL = todas)
    fk_materia_id       INT           NULL,      -- matéria alvo (NULL = todas)

    -- Papel-alvo: 'aluno', 'professor', 'coordenador', 'todos'
    papel_destino       VARCHAR(30)   NOT NULL DEFAULT 'todos',

    data_criacao        DATETIME      DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao    DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (fk_remetente_id) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (fk_turma_id)     REFERENCES turma(id)   ON DELETE SET NULL,
    FOREIGN KEY (fk_materia_id)   REFERENCES materia(id) ON DELETE SET NULL
);

-- ── 3. Tabela de destinatários individuais ───────────────────────
-- Gerada pelo backend no momento do envio: uma linha por usuário
-- que deve ver a mensagem. Armazena também se foi lido.
CREATE TABLE mensagem_destinatario (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    fk_mensagem_id     INT      NOT NULL,
    fk_usuario_id   INT      NOT NULL,         -- destinatário
    lido            BOOLEAN  DEFAULT FALSE,
    data_leitura    DATETIME NULL,

    UNIQUE (fk_mensagem_id, fk_usuario_id),

    FOREIGN KEY (fk_mensagem_id)   REFERENCES mensagem(id)    ON DELETE CASCADE,
    FOREIGN KEY (fk_usuario_id) REFERENCES usuario(id)  ON DELETE CASCADE
);

-- ── 4. Índices úteis ─────────────────────────────────────────────
CREATE INDEX idx_mensagem_remetente  ON mensagem (fk_remetente_id);
CREATE INDEX idx_mensagem_turma      ON mensagem (fk_turma_id);
CREATE INDEX idx_mensagem_destino    ON mensagem_destinatario (fk_usuario_id, lido);


-- ================================================================
-- Migração: Tabela curso + FK em turma  (versão corrigida)
-- Compatível com banco que já possui linhas na tabela turma
-- ================================================================

USE monitora;

-- ── 1. Cria tabela de cursos (já executado com sucesso, IF NOT EXISTS garante segurança) ──
CREATE TABLE IF NOT EXISTS curso (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    nome             VARCHAR(255) NOT NULL,
    codigo_prefixo   VARCHAR(20)  NOT NULL,
    ativo            BOOLEAN DEFAULT TRUE,
    data_criacao     DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ── 2. Insere os cursos ANTES de criar a FK (precisamos do id=1 existir) ──
INSERT IGNORE INTO curso (id, nome, codigo_prefixo) VALUES
    (1, 'Análise e Desenvolvimento de Sistemas', 'ADS'),
    (2, 'Engenharia de Software',                'ES'),
    (3, 'Ciência da Computação',                 'CC'),
    (4, 'Sistemas de Informação',                'SI');

-- ── 3. Remove coluna id_curso antiga (já executado; IF EXISTS evita erro ao rodar de novo) ──


-- ── 4. Adiciona fk_curso_id como NULL primeiro (para não quebrar linhas existentes) ──
ALTER TABLE turma
    ADD COLUMN fk_curso_id INT NULL AFTER id;

-- ── 5. Preenche as linhas existentes com o curso id=1 (ADS) como padrão ──
--      Ajuste o valor conforme necessário para cada turma existente.
UPDATE turma
SET fk_curso_id = 1
WHERE fk_curso_id IS NULL;

-- ── 6. Agora torna a coluna NOT NULL (todas as linhas já têm valor) ──
ALTER TABLE turma
    MODIFY COLUMN fk_curso_id INT NOT NULL;

-- ── 7. Aplica a constraint de chave estrangeira ──
ALTER TABLE turma
    ADD CONSTRAINT FK_turma_curso
    FOREIGN KEY (fk_curso_id)
    REFERENCES curso(id)
    ON DELETE RESTRICT;

-- ── 8. Adiciona coluna turma_letra (gerada pelo backend: A, B, C...) ──
ALTER TABLE turma
    ADD COLUMN  turma_letra VARCHAR(5) NOT NULL DEFAULT 'A' AFTER semestre;

-- ── 9. Migração do vínculo global professor_materia para o vínculo por turma ──
INSERT IGNORE INTO professor_turma_materia (fk_usuario_id, fk_turma_id, fk_materia_id)
SELECT
    pm.fk_usuario_id,
    mt.fk_turma_id,
    pm.fk_materia_id
FROM professor_materia pm
INNER JOIN materias_turma mt
    ON mt.fk_materia_id = pm.fk_materia_id;
