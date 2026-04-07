CREATE DATABASE IF NOT EXISTS monitora;

USE monitora;

CREATE TABLE usuario (
    id int PRIMARY KEY,
    nome nvarchar(255),
    email nvarchar(255),
    senha nvarchar(255),
    cpf nvarchar(14),
    data_nascimento date,
    telefone nvarchar(20),
    matricula nvarchar(50),
    especialidade nvarchar(255),
    salario decimal(10,2),
    ativo bit,
    data_criacao datetime,
    data_atualizacao datetime,
    fk_papel_id int
);

CREATE TABLE papel (
    id int PRIMARY KEY,
    descricao nvarchar(255),
    ativo bit,
    data_criacao datetime,
    data_atualizacao datetime
);

CREATE TABLE turma (
    id int PRIMARY KEY,
    id_curso int,
    nome nvarchar(255),
    codigo nvarchar(50),
    periodo int,
    ano int,
    semestre int,
    capacidade int,
    turno nvarchar(20),
    ativo bit,
    data_criacao datetime,
    data_atualizacao datetime
);

CREATE TABLE nota (
    id int PRIMARY KEY,
    valor decimal(5,2),
    observacao nvarchar(255),
    data_lancamento datetime,
    data_criacao datetime,
    data_atualizacao datetime,
    fk_materia_id int,
    fk_usuario_id int
);

CREATE TABLE materia (
    id int PRIMARY KEY,
    nome nvarchar(255),
    codigo nvarchar(50),
    carga_horaria int,
    descricao nvarchar(500),
    ativo bit,
    data_criacao datetime,
    data_atualizacao datetime
);

CREATE TABLE frequencia (
    id int PRIMARY KEY,
    data_aula date,
    presente bit,
    justificativa nvarchar(255),
    data_criacao datetime,
    data_atualizacao datetime,
    fk_usuario_id int,
    fk_materia_id int
);

CREATE TABLE aviso (
    id int PRIMARY KEY,
    titulo nvarchar(255),
    descricao nvarchar(1000),
    data_publicacao datetime,
    ativo bit,
    data_criacao datetime,
    data_atualizacao datetime
);

-- ---------------------------------------

CREATE TABLE usuario_turma (
    fk_usuario_id int,
    fk_turma_id int
);

CREATE TABLE materia_aviso (
    fk_materia_id int,
    fk_aviso_id int
);

CREATE TABLE materias_turma (
    fk_materia_id int,
    fk_turma_id int
);

CREATE TABLE professor_materia (
    fk_usuario_id int,
    fk_materia_id int
);

-- ---------------------------------------

-- usuario -> papel
ALTER TABLE usuario ADD CONSTRAINT FK_usuario_papel
FOREIGN KEY (fk_papel_id)
REFERENCES papel (id)
ON DELETE CASCADE;

-- nota
ALTER TABLE nota ADD CONSTRAINT FK_nota_materia
FOREIGN KEY (fk_materia_id)
REFERENCES materia (id)
ON DELETE CASCADE;

ALTER TABLE nota ADD CONSTRAINT FK_nota_usuario
FOREIGN KEY (fk_usuario_id)
REFERENCES usuario (id)
ON DELETE CASCADE;

-- frequencia
ALTER TABLE frequencia ADD CONSTRAINT FK_frequencia_usuario
FOREIGN KEY (fk_usuario_id)
REFERENCES usuario (id)
ON DELETE CASCADE;

ALTER TABLE frequencia ADD CONSTRAINT FK_frequencia_materia
FOREIGN KEY (fk_materia_id)
REFERENCES materia (id)
ON DELETE CASCADE;

-- usuario_turma
ALTER TABLE usuario_turma ADD CONSTRAINT FK_usuario_turma_usuario
FOREIGN KEY (fk_usuario_id)
REFERENCES usuario (id)
ON DELETE CASCADE;

ALTER TABLE usuario_turma ADD CONSTRAINT FK_usuario_turma_turma
FOREIGN KEY (fk_turma_id)
REFERENCES turma (id)
ON DELETE CASCADE;

-- materia_aviso
ALTER TABLE materia_aviso ADD CONSTRAINT FK_materia_aviso_materia
FOREIGN KEY (fk_materia_id)
REFERENCES materia (id)
ON DELETE CASCADE;

ALTER TABLE materia_aviso ADD CONSTRAINT FK_materia_aviso_aviso
FOREIGN KEY (fk_aviso_id)
REFERENCES aviso (id)
ON DELETE CASCADE;

-- materias_turma
ALTER TABLE materias_turma ADD CONSTRAINT FK_materias_turma_materia
FOREIGN KEY (fk_materia_id)
REFERENCES materia (id)
ON DELETE CASCADE;

ALTER TABLE materias_turma ADD CONSTRAINT FK_materias_turma_turma
FOREIGN KEY (fk_turma_id)
REFERENCES turma (id)
ON DELETE CASCADE;

-- professor_materia
ALTER TABLE professor_materia ADD CONSTRAINT FK_professor_materia_usuario
FOREIGN KEY (fk_usuario_id)
REFERENCES usuario (id)
ON DELETE CASCADE;

ALTER TABLE professor_materia ADD CONSTRAINT FK_professor_materia_materia
FOREIGN KEY (fk_materia_id)
REFERENCES materia (id)
ON DELETE CASCADE;
