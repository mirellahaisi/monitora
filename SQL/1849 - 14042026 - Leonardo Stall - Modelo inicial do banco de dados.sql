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