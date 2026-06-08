-- ================================================================
-- Monitora+ — Banco de Dados
-- Versão para desenvolvimento colaborativo
-- ================================================================
--
-- Usuários de acesso:
--   Coordenador : carlos@monitora.com   / senha: 1234567
--   Professor   : ana@monitora.com      / senha: 123456
--   Aluno       : joao@monitora.com     / senha: 123456
--   Aluno       : mariana@monitora.com  / senha: 123456
--
-- (Senha padrão = data de nascimento no formato DDMMAA)
-- ================================================================

DROP DATABASE IF EXISTS monitora;
CREATE DATABASE monitora CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE monitora;

/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- ================================================================
-- TABELAS INDEPENDENTES (sem FK)
-- ================================================================

-- ----------------------------------------------------------------
-- papel
-- Papéis do sistema: ADMIN (coordenação), Professor, Aluno
-- ----------------------------------------------------------------
CREATE TABLE `papel` (
  `id`               int          NOT NULL AUTO_INCREMENT,
  `descricao`        varchar(255) DEFAULT NULL,
  `ativo`            tinyint(1)   DEFAULT NULL,
  `data_criacao`     datetime     DEFAULT CURRENT_TIMESTAMP,
  `data_atualizacao` datetime     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `papel` VALUES
  (1, 'ADMIN',     1, '2026-04-14 19:11:21', '2026-04-14 19:11:21'),
  (2, 'Professor', 1, '2026-04-14 19:11:21', '2026-04-14 19:11:21'),
  (3, 'Aluno',     1, '2026-04-14 19:11:21', '2026-04-14 19:11:21');


-- ----------------------------------------------------------------
-- curso
-- ----------------------------------------------------------------
CREATE TABLE `curso` (
  `id`               int          NOT NULL AUTO_INCREMENT,
  `nome`             varchar(255) NOT NULL,
  `codigo_prefixo`   varchar(20)  NOT NULL,
  `ativo`            tinyint(1)   DEFAULT '1',
  `data_criacao`     datetime     DEFAULT CURRENT_TIMESTAMP,
  `data_atualizacao` datetime     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `curso` VALUES
  (1, 'Análise e Desenvolvimento de Sistemas', 'ADS', 0, '2026-06-04 22:15:24', '2026-06-05 04:02:19'),
  (2, 'Engenharia de Software',                'ES',  1, '2026-06-04 22:15:24', '2026-06-04 22:15:24'),
  (3, 'Ciência da Computação',                 'CC',  1, '2026-06-04 22:15:24', '2026-06-04 22:15:24'),
  (4, 'Sistemas de Informação',                'SI',  1, '2026-06-04 22:15:24', '2026-06-04 22:15:24');


-- ----------------------------------------------------------------
-- materia
-- ----------------------------------------------------------------
CREATE TABLE `materia` (
  `id`               int          NOT NULL AUTO_INCREMENT,
  `nome`             varchar(255) DEFAULT NULL,
  `codigo`           varchar(50)  DEFAULT NULL,
  `carga_horaria`    int          DEFAULT NULL,
  `descricao`        varchar(500) DEFAULT NULL,
  `ativo`            tinyint(1)   DEFAULT NULL,
  `data_criacao`     datetime     DEFAULT CURRENT_TIMESTAMP,
  `data_atualizacao` datetime     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `materia` VALUES
  (1, 'Banco de Dados',      'BD101',  80, 'Introdução a banco de dados relacionais', 1, '2026-04-14 19:11:21', '2026-04-14 19:11:21'),
  (2, 'Algoritmos',          'ALG101', 80, 'Lógica de programação',                   1, '2026-04-14 19:11:21', '2026-04-14 19:11:21'),
  (3, 'Estrutura de Dados',  'ED201',  80, 'Estruturas básicas',                      1, '2026-04-14 19:11:21', '2026-04-14 19:11:21');


-- ================================================================
-- USUÁRIOS
-- ================================================================

-- ----------------------------------------------------------------
-- usuario
-- 4 usuários de demonstração (1 por papel + 1 aluno extra).
-- Senhas geradas via scrypt pelo próprio sistema (padrão = DDMMAA).
-- ----------------------------------------------------------------
CREATE TABLE `usuario` (
  `id`               int             NOT NULL AUTO_INCREMENT,
  `nome`             varchar(255)    DEFAULT NULL,
  `email`            varchar(255)    DEFAULT NULL,
  `senha`            varchar(255)    DEFAULT NULL,
  `cpf`              varchar(14)     DEFAULT NULL,
  `data_nascimento`  date            DEFAULT NULL,
  `telefone`         varchar(20)     DEFAULT NULL,
  `especialidade`    varchar(255)    DEFAULT NULL,
  `salario`          decimal(10,2)   DEFAULT NULL,
  `ativo`            tinyint(1)      DEFAULT NULL,
  `data_criacao`     datetime        DEFAULT CURRENT_TIMESTAMP,
  `data_atualizacao` datetime        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `fk_papel_id`      int             DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `cpf`   (`cpf`),
  KEY `FK_usuario_papel` (`fk_papel_id`),
  CONSTRAINT `FK_usuario_papel` FOREIGN KEY (`fk_papel_id`) REFERENCES `papel` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `usuario` VALUES
  -- Coordenador/Admin  (senha: 050195 → data de nasc. 1995-01-05)
  (1, 'Carlos Silva Andrade', 'carlos@monitora.com',
   'scrypt:32768:8:1$vM9oRIv0aopZx5VJ$4cb9cb595d9550462ca9b4fc87cf6e744c44e0db94b0cb1227d5c847bc40fed5ebf966dfe30089bde46059497b788ab32ca9832ec33a152d2c618ebeaa78b087',
   '12345678900', '1995-01-05', '41999990001', 'Gestão',     5000.00, 1, '2026-04-14 19:11:21', '2026-04-14 19:11:21', 1),

  -- Professor  (senha: 200885 → data de nasc. 1985-08-20)
  (2, 'Ana Souza',            'ana@monitora.com',
   'scrypt:32768:8:1$5MQ12oY7BPOcGf9q$23a0777d2657ef49c2b41f6e6baa7a58280b3a12ceb8f9f30ed89b0cf9ad6e0aa9053accc980eed45f77974737c3ccf913f21528d77e97c2f02553cff18728b4',
   '98765432100', '1985-08-20', '41999990002', 'Matemática', 7000.00, 1, '2026-04-14 19:11:21', '2026-04-14 19:11:21', 2),

  -- Aluno  (senha: 150303 → data de nasc. 2003-03-15)
  (3, 'João Pereira',         'joao@monitora.com',
   '123456',
   '11122233344', '2003-03-15', '41999990003', NULL, NULL, 1, '2026-04-14 19:11:21', '2026-04-14 19:11:21', 3),

  -- Aluno  (senha: 251102 → data de nasc. 2002-11-25)
  (4, 'Mariana Lima',         'mariana@monitora.com',
   'scrypt:32768:8:1$LlHrxlXldMrB4HyA$c75e0aa07155e417f6616a1af246c54f04dcd5707f031a38a9f5c0c0fa32b421aae9bb255945e3fc3bd0bbc11388eb90684f815325f847db49411f7ac478ae76',
   '55566677788', '2002-11-25', '41999990004', NULL, NULL, 1, '2026-04-14 19:11:21', '2026-04-14 19:11:21', 3);


-- ================================================================
-- TURMAS
-- ================================================================

-- ----------------------------------------------------------------
-- turma
-- ----------------------------------------------------------------
CREATE TABLE `turma` (
  `id`               int          NOT NULL AUTO_INCREMENT,
  `fk_curso_id`      int          NOT NULL,
  `nome`             varchar(255) DEFAULT NULL,
  `codigo`           varchar(50)  DEFAULT NULL,
  `periodo`          int          DEFAULT NULL,
  `ano`              int          DEFAULT NULL,
  `semestre`         int          DEFAULT NULL,
  `turma_letra`      varchar(5)   NOT NULL DEFAULT 'A',
  `capacidade`       int          DEFAULT NULL,
  `turno`            varchar(20)  DEFAULT NULL,
  `ativo`            tinyint(1)   DEFAULT NULL,
  `data_criacao`     datetime     DEFAULT CURRENT_TIMESTAMP,
  `data_atualizacao` datetime     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `turma` VALUES
  (1, 4, 'SI 2026.1 — Noite',                    'SI-2026-1-NA',  1, 2026, 1, 'A', 40, 'Noite', 1, '2026-04-14 19:11:21', '2026-04-14 19:11:21'),
  (2, 4, 'Sistemas de Informação - 2º Período',   'SI-2026-2',     2, 2026, 1, 'A', 40, 'Noite', 1, '2026-04-14 19:11:21', '2026-04-14 19:11:21'),
  (4, 1, 'ADS 2026.1 — 4º Período — Noite',       'ADS-2026-1-NA', 4, 2026, 1, 'A',  5, 'Noite', 1, '2026-06-04 22:18:59', '2026-06-04 22:18:59'),
  (5, 3, 'CC 2026.2 - Noite B',                   'CC-2026-2-NB', 10, 2026, 2, 'B',  5, 'Noite', 1, '2026-06-04 22:20:02', '2026-06-04 22:20:02'),
  (6, 1, 'ADS 2026.1 — 4º Período — Noite (B)',   'ADS-2026-1-NB', 4, 2026, 1, 'B', 20, 'Noite', 0, '2026-06-04 22:20:25', '2026-06-04 22:20:25'),
  (8, 3, 'CC 2026.2 - Noite',                     'CC-2026-2-NA', 10, 2026, 2, 'A',  1, 'Noite', 1, '2026-06-04 22:45:11', '2026-06-04 22:45:11');


-- ================================================================
-- VÍNCULOS: USUÁRIO ↔ TURMA / PROFESSOR ↔ MATÉRIA
-- ================================================================

-- ----------------------------------------------------------------
-- usuario_turma
-- Cada aluno em exatamente uma turma ativa.
-- ----------------------------------------------------------------
CREATE TABLE `usuario_turma` (
  `id`           int NOT NULL AUTO_INCREMENT,
  `fk_usuario_id` int DEFAULT NULL,
  `fk_turma_id`  int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fk_usuario_id` (`fk_usuario_id`, `fk_turma_id`),
  KEY `fk_turma_id` (`fk_turma_id`),
  CONSTRAINT `usuario_turma_ibfk_1` FOREIGN KEY (`fk_usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE,
  CONSTRAINT `usuario_turma_ibfk_2` FOREIGN KEY (`fk_turma_id`)   REFERENCES `turma`   (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `usuario_turma` VALUES
  (2, 4, 1),   -- Mariana → turma 1 (SI 2026.1 Noite)
  (8, 3, 1);   -- João    → turma 1 (SI 2026.1 Noite)


-- ----------------------------------------------------------------
-- professor_materia
-- Vínculo legado mantido para compatibilidade com o backend.
-- Gerenciado automaticamente por _sincronizar_professor_materia_legado().
-- ----------------------------------------------------------------
CREATE TABLE `professor_materia` (
  `id`             int NOT NULL AUTO_INCREMENT,
  `fk_usuario_id`  int DEFAULT NULL,
  `fk_materia_id`  int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fk_usuario_id` (`fk_usuario_id`, `fk_materia_id`),
  KEY `fk_materia_id` (`fk_materia_id`),
  CONSTRAINT `professor_materia_ibfk_1` FOREIGN KEY (`fk_usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE,
  CONSTRAINT `professor_materia_ibfk_2` FOREIGN KEY (`fk_materia_id`) REFERENCES `materia` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `professor_materia` VALUES
  (1, 2, 1),   -- Ana → Banco de Dados
  (2, 2, 2),   -- Ana → Algoritmos
  (8, 2, 3);   -- Ana → Estrutura de Dados


-- ----------------------------------------------------------------
-- materias_turma
-- Nota: BD (materia 1) adicionado à turma 1 para consistir com
-- eventos e mensagens de demonstração que a referenciam.
-- ----------------------------------------------------------------
CREATE TABLE `materias_turma` (
  `id`            int NOT NULL AUTO_INCREMENT,
  `fk_materia_id` int DEFAULT NULL,
  `fk_turma_id`   int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fk_materia_id` (`fk_materia_id`, `fk_turma_id`),
  KEY `fk_turma_id` (`fk_turma_id`),
  CONSTRAINT `materias_turma_ibfk_1` FOREIGN KEY (`fk_materia_id`) REFERENCES `materia` (`id`) ON DELETE CASCADE,
  CONSTRAINT `materias_turma_ibfk_2` FOREIGN KEY (`fk_turma_id`)   REFERENCES `turma`   (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `materias_turma` (id, fk_materia_id, fk_turma_id) VALUES
  -- Turma 1: SI 2026.1 Noite
  (17, 1, 1),   -- Banco de Dados
  (12, 2, 1),   -- Algoritmos

  -- Turma 2: SI 2026 2º Período
  (11, 1, 2),   -- Banco de Dados
  ( 9, 2, 2),   -- Algoritmos

  -- Turma 4: ADS 2026.1 Noite
  ( 7, 2, 4),   -- Algoritmos

  -- Turma 5: CC 2026.2 Noite B
  (13, 1, 5),   -- Banco de Dados
  ( 8, 2, 5),   -- Algoritmos
  (14, 3, 5),   -- Estrutura de Dados

  -- Turma 8: CC 2026.2 Noite
  (10, 1, 8),   -- Banco de Dados
  (15, 2, 8);   -- Algoritmos


-- ----------------------------------------------------------------
-- professor_turma_materia
-- Nota: Ana adicionada como professora de BD na turma 1
-- para consistir com eventos e mensagens de demonstração.
-- ----------------------------------------------------------------
CREATE TABLE `professor_turma_materia` (
  `id`             int NOT NULL AUTO_INCREMENT,
  `fk_usuario_id`  int NOT NULL,
  `fk_turma_id`    int NOT NULL,
  `fk_materia_id`  int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fk_usuario_id` (`fk_usuario_id`, `fk_turma_id`, `fk_materia_id`),
  KEY `fk_turma_id`   (`fk_turma_id`),
  KEY `fk_materia_id` (`fk_materia_id`),
  CONSTRAINT `professor_turma_materia_ibfk_1` FOREIGN KEY (`fk_usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE,
  CONSTRAINT `professor_turma_materia_ibfk_2` FOREIGN KEY (`fk_turma_id`)   REFERENCES `turma`   (`id`) ON DELETE CASCADE,
  CONSTRAINT `professor_turma_materia_ibfk_3` FOREIGN KEY (`fk_materia_id`) REFERENCES `materia` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `professor_turma_materia` (id, fk_usuario_id, fk_turma_id, fk_materia_id) VALUES
  -- Turma 1: SI 2026.1 Noite
  (17, 2, 1, 1),   -- Ana → Banco de Dados
  ( 5, 2, 1, 2),   -- Ana → Algoritmos

  -- Turma 2: SI 2026 2º Período
  ( 1, 2, 2, 1),   -- Ana → Banco de Dados
  ( 6, 2, 2, 2),   -- Ana → Algoritmos

  -- Turma 4: ADS 2026.1 Noite
  ( 8, 2, 4, 2),   -- Ana → Algoritmos

  -- Turma 5: CC 2026.2 Noite B
  ( 3, 2, 5, 1),   -- Ana → Banco de Dados
  ( 9, 2, 5, 2),   -- Ana → Algoritmos
  (11, 2, 5, 3),   -- Ana → Estrutura de Dados

  -- Turma 8: CC 2026.2 Noite
  ( 4, 2, 8, 1),   -- Ana → Banco de Dados
  (16, 2, 8, 2);   -- Ana → Algoritmos


-- ================================================================
-- ACADÊMICO: NOTAS E FREQUÊNCIA
-- ================================================================

-- ----------------------------------------------------------------
-- nota
-- ----------------------------------------------------------------
CREATE TABLE `nota` (
  `id`               int           NOT NULL AUTO_INCREMENT,
  `valor`            decimal(5,2)  DEFAULT NULL,
  `observacao`       varchar(255)  DEFAULT NULL,
  `data_lancamento`  datetime      DEFAULT NULL,
  `data_criacao`     datetime      DEFAULT CURRENT_TIMESTAMP,
  `data_atualizacao` datetime      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `fk_materia_id`    int           DEFAULT NULL,
  `fk_usuario_id`    int           DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_materia_id` (`fk_materia_id`),
  KEY `fk_usuario_id` (`fk_usuario_id`),
  CONSTRAINT `nota_ibfk_1` FOREIGN KEY (`fk_materia_id`) REFERENCES `materia`  (`id`) ON DELETE CASCADE,
  CONSTRAINT `nota_ibfk_2` FOREIGN KEY (`fk_usuario_id`) REFERENCES `usuario`  (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `nota` VALUES
  -- João — Banco de Dados
  ( 1,  8.50, 'nota1', '2026-04-14 19:11:21', '2026-04-14 19:11:21', '2026-04-14 19:11:21', 1, 3),
  ( 8, 10.00, 'nota2', '2026-05-04 16:11:03', '2026-05-04 16:11:03', '2026-05-04 16:11:03', 1, 3),
  -- João — Algoritmos
  ( 2,  7.00, 'nota1', '2026-04-14 19:11:21', '2026-04-14 19:11:21', '2026-04-14 19:11:21', 2, 3),
  ( 4,  2.00, 'nota2', '2026-05-04 15:41:45', '2026-05-04 15:40:51', '2026-05-04 15:41:45', 2, 3),

  -- Mariana — Banco de Dados
  ( 3,  9.00, 'nota1', '2026-04-14 19:11:21', '2026-04-14 19:11:21', '2026-04-14 19:11:21', 1, 4),
  (10,  2.00, 'nota2', '2026-05-04 16:11:03', '2026-05-04 16:11:03', '2026-05-04 16:11:03', 1, 4),
  -- Mariana — Algoritmos
  ( 6,  0.10, 'nota1', '2026-06-04 21:42:36', '2026-05-04 15:40:51', '2026-06-04 21:42:36', 2, 4),
  ( 7,  0.00, 'nota2', '2026-06-04 21:42:36', '2026-05-04 15:40:51', '2026-06-04 21:42:36', 2, 4);


-- ----------------------------------------------------------------
-- frequencia
-- ----------------------------------------------------------------
CREATE TABLE `frequencia` (
  `id`               int          NOT NULL AUTO_INCREMENT,
  `data_aula`        date         DEFAULT NULL,
  `presente`         tinyint(1)   DEFAULT NULL,
  `justificativa`    varchar(255) DEFAULT NULL,
  `data_criacao`     datetime     DEFAULT CURRENT_TIMESTAMP,
  `data_atualizacao` datetime     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `fk_usuario_id`    int          DEFAULT NULL,
  `fk_materia_id`    int          DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_usuario_id` (`fk_usuario_id`),
  KEY `fk_materia_id` (`fk_materia_id`),
  CONSTRAINT `frequencia_ibfk_1` FOREIGN KEY (`fk_usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE,
  CONSTRAINT `frequencia_ibfk_2` FOREIGN KEY (`fk_materia_id`) REFERENCES `materia` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `frequencia` VALUES
  -- Banco de Dados
  ( 1, '2026-03-10', 1, NULL,         '2026-04-14 19:11:21', '2026-04-14 19:11:21', 3, 1),  -- João presente
  ( 2, '2026-03-10', 0, 'Atestado médico', '2026-04-14 19:11:21', '2026-04-14 19:11:21', 4, 1),  -- Mariana falta
  (10, '2026-05-04', 1, '',           '2026-05-18 16:59:43', '2026-05-18 16:59:43', 3, 1),  -- João presente
  (11, '2026-05-04', 1, '',           '2026-05-18 16:59:43', '2026-05-18 16:59:43', 4, 1),  -- Mariana presente
  (14, '2026-05-26', 1, '',           '2026-05-25 15:30:51', '2026-05-25 15:30:51', 3, 1),  -- João presente
  (15, '2026-05-26', 0, '',           '2026-05-25 15:30:51', '2026-05-25 15:30:51', 4, 1),  -- Mariana falta

  -- Algoritmos
  ( 3, '2026-03-11', 1, NULL,         '2026-04-14 19:11:21', '2026-04-14 19:11:21', 3, 2),  -- João presente
  ( 4, '2026-05-19', 1, '',           '2026-05-18 16:21:47', '2026-05-18 17:05:14', 3, 2),  -- João presente
  ( 5, '2026-05-19', 0, '',           '2026-05-18 16:21:47', '2026-05-18 17:05:14', 4, 2),  -- Mariana falta
  ( 6, '2026-05-23', 1, '',           '2026-05-18 16:22:57', '2026-05-18 16:22:57', 3, 2),  -- João presente
  ( 7, '2026-05-23', 1, '',           '2026-05-18 16:22:57', '2026-05-18 16:22:57', 4, 2),  -- Mariana presente
  ( 8, '2026-05-20', 0, 'Justificativa', '2026-05-18 16:53:32', '2026-05-20 19:21:48', 3, 2),  -- João falta
  ( 9, '2026-05-20', 0, 'Justificativa', '2026-05-18 16:53:32', '2026-05-20 19:21:48', 4, 2),  -- Mariana falta
  (12, '2026-05-12', 1, '',           '2026-05-18 17:04:59', '2026-05-18 17:04:59', 3, 2),  -- João presente
  (13, '2026-05-12', 0, '',           '2026-05-18 17:04:59', '2026-05-18 17:04:59', 4, 2),  -- Mariana falta
  (16, '2026-06-12', 1, '',           '2026-06-02 18:29:13', '2026-06-02 18:29:13', 3, 2),  -- João presente
  (17, '2026-06-02', 1, 'Presente',   '2026-06-04 21:50:10', '2026-06-04 21:50:10', 4, 2);  -- Mariana presente


-- ================================================================
-- COMUNICAÇÃO: MENSAGENS E CALENDÁRIO
-- ================================================================

-- ----------------------------------------------------------------
-- mensagem
-- ----------------------------------------------------------------
CREATE TABLE `mensagem` (
  `id`               int          NOT NULL AUTO_INCREMENT,
  `titulo`           varchar(255) NOT NULL,
  `descricao`        text         NOT NULL,
  `data_publicacao`  datetime     DEFAULT CURRENT_TIMESTAMP,
  `ativo`            tinyint(1)   DEFAULT '1',
  `fk_remetente_id`  int          NOT NULL,
  `fk_turma_id`      int          DEFAULT NULL,
  `fk_materia_id`    int          DEFAULT NULL,
  `papel_destino`    varchar(30)  NOT NULL DEFAULT 'todos',
  `data_criacao`     datetime     DEFAULT CURRENT_TIMESTAMP,
  `data_atualizacao` datetime     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_materia_id`         (`fk_materia_id`),
  KEY `idx_mensagem_remetente` (`fk_remetente_id`),
  KEY `idx_mensagem_turma`     (`fk_turma_id`),
  CONSTRAINT `mensagem_ibfk_1` FOREIGN KEY (`fk_remetente_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE,
  CONSTRAINT `mensagem_ibfk_2` FOREIGN KEY (`fk_turma_id`)     REFERENCES `turma`   (`id`) ON DELETE SET NULL,
  CONSTRAINT `mensagem_ibfk_3` FOREIGN KEY (`fk_materia_id`)   REFERENCES `materia` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `mensagem` VALUES
  (1, 'Prova de Banco de Dados',
   'A prova de BD será realizada na próxima semana, quinta-feira às 19h. Revejam normalização e SQL avançado.',
   '2026-05-29 20:47:30', 1, 1, 1, 1, 'aluno',       '2026-05-29 20:47:30', '2026-05-29 20:47:30'),

  (2, 'Entrega do Trabalho de Algoritmos',
   'Lembrem-se: a entrega é até sexta-feira às 23h59 pelo portal. Sem prorrogação.',
   '2026-05-27 20:47:30', 1, 2, 1, 2, 'aluno',       '2026-05-29 20:47:30', '2026-05-29 20:47:30'),

  (3, 'Reunião Pedagógica',
   'Reunião pedagógica na segunda-feira às 18h na sala dos professores. Presença obrigatória.',
   '2026-05-28 20:47:30', 1, 1, NULL, NULL, 'professor', '2026-05-29 20:47:30', '2026-05-29 20:47:30'),

  (4, 'Dúvida sobre conteúdo da prova',
   'Professora, o conteúdo de índices e views cai na prova de BD? Não encontrei no cronograma.',
   '2026-05-29 17:47:30', 1, 3, 1, 1, 'professor',   '2026-05-29 20:47:30', '2026-05-29 20:47:30'),

  (5, 'Recesso de Maio',
   'Nos dias 29 e 30 de maio não haverá aulas. As aulas retornam em 02 de junho. Bom descanso!',
   '2026-05-24 20:47:30', 1, 1, 1, NULL, 'todos',    '2026-05-29 20:47:30', '2026-05-29 20:47:30'),

  (6, 'Solicitação de material didático',
   'Coordenador, solicito a aquisição de licenças do MySQL Workbench para o laboratório.',
   '2026-05-29 16:47:30', 1, 2, NULL, NULL, 'coordenador', '2026-05-29 20:47:30', '2026-05-29 20:47:30');


-- ----------------------------------------------------------------
-- mensagem_destinatario
-- ----------------------------------------------------------------
CREATE TABLE `mensagem_destinatario` (
  `id`               int      NOT NULL AUTO_INCREMENT,
  `fk_mensagem_id`   int      NOT NULL,
  `fk_usuario_id`    int      NOT NULL,
  `lido`             tinyint(1) DEFAULT '0',
  `data_leitura`     datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fk_mensagem_id` (`fk_mensagem_id`, `fk_usuario_id`),
  KEY `idx_mensagem_destino` (`fk_usuario_id`, `lido`),
  CONSTRAINT `mensagem_destinatario_ibfk_1` FOREIGN KEY (`fk_mensagem_id`) REFERENCES `mensagem` (`id`) ON DELETE CASCADE,
  CONSTRAINT `mensagem_destinatario_ibfk_2` FOREIGN KEY (`fk_usuario_id`)  REFERENCES `usuario`  (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `mensagem_destinatario` VALUES
  ( 1, 1, 3, 1, '2026-05-29 19:47:30'),  -- João leu msg 1
  ( 2, 1, 4, 1, '2026-05-29 20:00:00'),  -- Mariana leu msg 1
  ( 3, 2, 3, 1, '2026-05-29 18:47:30'),  -- João leu msg 2
  ( 4, 2, 4, 1, '2026-05-29 19:00:00'),  -- Mariana leu msg 2
  ( 5, 3, 2, 1, '2026-05-29 20:17:30'),  -- Ana leu msg 3
  ( 6, 4, 2, 1, '2026-05-29 20:47:52'),  -- Ana leu msg 4
  ( 7, 5, 3, 1, '2026-05-30 16:09:49'),  -- João leu msg 5
  ( 8, 5, 4, 1, '2026-05-30 16:09:49'),  -- Mariana leu msg 5
  ( 9, 5, 2, 1, '2026-05-30 16:09:49'),  -- Ana leu msg 5
  (10, 6, 1, 1, '2026-06-02 14:42:33');  -- Carlos leu msg 6


-- ----------------------------------------------------------------
-- evento_calendario
-- ----------------------------------------------------------------
CREATE TABLE `evento_calendario` (
  `id`               int           NOT NULL AUTO_INCREMENT,
  `titulo`           varchar(255)  NOT NULL,
  `descricao`        varchar(1000) DEFAULT NULL,
  `data_inicio`      datetime      NOT NULL,
  `data_fim`         datetime      DEFAULT NULL,
  `cor`              varchar(20)   DEFAULT '#4caebe',
  `tipo`             varchar(30)   DEFAULT 'evento',
  `ativo`            tinyint(1)    DEFAULT '1',
  `data_criacao`     datetime      DEFAULT CURRENT_TIMESTAMP,
  `data_atualizacao` datetime      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `fk_criador_id`    int           NOT NULL,
  `fk_turma_id`      int           DEFAULT NULL,
  `fk_materia_id`    int           DEFAULT NULL,
  `visibilidade`     enum('todos','alunos','professores') NOT NULL DEFAULT 'todos',
  `pessoal`          tinyint(1)    NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `fk_criador_id` (`fk_criador_id`),
  KEY `fk_turma_id`   (`fk_turma_id`),
  KEY `fk_materia_id` (`fk_materia_id`),
  CONSTRAINT `evento_calendario_ibfk_1` FOREIGN KEY (`fk_criador_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE,
  CONSTRAINT `evento_calendario_ibfk_2` FOREIGN KEY (`fk_turma_id`)   REFERENCES `turma`   (`id`) ON DELETE SET NULL,
  CONSTRAINT `evento_calendario_ibfk_3` FOREIGN KEY (`fk_materia_id`) REFERENCES `materia` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `evento_calendario` VALUES
  -- Eventos da coordenação (Carlos, fk_criador_id=1)
  (40, 'Reunião pedagógica geral',        'Reunião obrigatória para professores e alunos. Sala Magna às 19h.',              '2026-06-02 19:00:00', '2026-06-02 21:00:00', '#4caebe', 'aviso',   1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 1, NULL, NULL, 'todos',       0),
  (41, 'Semana acadêmica 2026',           'Programação completa disponível no mural. Participação de todos os cursos.',     '2026-06-09 08:00:00', '2026-06-13 18:00:00', '#8e44ad', 'evento',  1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 1, NULL, NULL, 'todos',       0),
  (42, 'Formatura SI – 1º Período',       'Cerimônia de formatura da turma do 1º período.',                                 '2026-06-20 18:00:00', '2026-06-20 22:00:00', '#57dbbd', 'evento',  1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 1, 1,    NULL, 'todos',       0),
  (43, 'Prazo de rematrícula',            'Último dia para rematrícula no portal do aluno. Não perca o prazo!',             '2026-06-05 23:59:00', NULL,                  '#e67e22', 'aviso',   1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 1, NULL, NULL, 'alunos',      0),
  (44, 'Entrega de diários de classe',    'Todos os professores devem entregar os diários atualizados até esta data.',      '2026-06-06 17:00:00', NULL,                  '#c0392b', 'entrega', 1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 1, NULL, NULL, 'professores', 0),
  (45, 'Capacitação: uso do Monitora+',   'Treinamento para professores sobre os novos recursos do sistema.',               '2026-06-10 14:00:00', '2026-06-10 17:00:00', '#2980b9', 'evento',  1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 1, NULL, NULL, 'professores', 0),
  (46, 'Renovar contrato docente',        'Professores do 1º período devem renovar contrato até sexta.',                   '2026-06-12 08:00:00', NULL,                  '#7a96a8', 'aviso',   1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 1, 1,    NULL, 'professores', 0),

  -- Eventos da professora (Ana, fk_criador_id=2)
  (47, 'Aula de revisão – Algoritmos',    'Revisão de vetores, matrizes e funções recursivas antes da prova.',             '2026-06-03 19:00:00', '2026-06-03 20:30:00', '#1abc9c', 'aula',    1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 2, 1, NULL, 'alunos', 0),
  (48, 'Monitoria de Banco de Dados',     'Sessão de monitoria aberta para alunos com dificuldades na disciplina.',        '2026-06-04 18:00:00', '2026-06-04 20:00:00', '#2ecc71', 'aula',    1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 2, 1, 1,    'alunos', 0),
  (49, 'Prova 1 – Banco de Dados',        'Conteúdo: modelagem ER, normalização até 3FN e SQL básico. Trazer caneta.',     '2026-06-11 19:30:00', '2026-06-11 21:00:00', '#e74c3c', 'prova',   1, '2026-05-29 18:46:28', '2026-05-29 18:56:34', 2, NULL, NULL, 'alunos', 1),
  (50, 'Entrega – Trabalho de Algoritmos','Enviar o arquivo .zip pelo portal até meia-noite. Sem prorrogação.',            '2026-06-07 23:59:00', NULL,                  '#f39c12', 'entrega', 1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 2, 1, 2,    'alunos', 0),
  (51, 'Prova 1 – Algoritmos',            'Conteúdo: estruturas de repetição, funções e vetores.',                         '2026-06-18 19:30:00', '2026-06-18 21:00:00', '#e74c3c', 'prova',   1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 2, 1, 2,    'alunos', 0),

  -- Eventos pessoais dos alunos
  (52, 'Estudar normalização',            'Revisar slides da aula 4 e resolver os exercícios do livro.',                   '2026-06-03 20:00:00', '2026-06-03 22:00:00', '#57dbbd', 'evento',  1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 3, NULL, NULL, 'todos', 1),
  (53, 'Grupo de estudos com Mariana',    'Encontro na biblioteca para preparar o trabalho de Algoritmos.',                '2026-06-05 18:00:00', '2026-06-05 20:00:00', '#8e44ad', 'evento',  1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 3, NULL, NULL, 'todos', 1),
  (54, 'Consulta médica',                 'UBS – lembrar de levar carteirinha.',                                           '2026-06-12 15:00:00', NULL,                  '#7a96a8', 'evento',  1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 3, NULL, NULL, 'todos', 1),
  (55, 'Revisar SQL – prova semana que vem', 'Foco em JOINs e subconsultas. Ver vídeo aula no YouTube.',                  '2026-06-08 19:00:00', '2026-06-08 21:00:00', '#57dbbd', 'evento',  1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 4, NULL, NULL, 'todos', 1),
  (56, 'Lembrete: entregar trabalho',     'Não esquecer de enviar o zip antes da meia-noite do dia 7!',                   '2026-06-07 08:00:00', NULL,                  '#e67e22', 'aviso',   1, '2026-05-29 18:46:28', '2026-05-29 18:46:28', 4, NULL, NULL, 'todos', 1);


-- ================================================================
-- ÍNDICES
-- Verificados contra todas as queries do backend Flask.
-- ================================================================

CREATE INDEX idx_turma_curso            ON turma(fk_curso_id);
CREATE INDEX idx_usuario_ativo          ON usuario(ativo);
CREATE INDEX idx_turma_ativo            ON turma(ativo);
CREATE INDEX idx_materia_ativo          ON materia(ativo);
CREATE INDEX idx_evento_data            ON evento_calendario(data_inicio, data_fim);
CREATE INDEX idx_evento_visibilidade_data ON evento_calendario(visibilidade, data_inicio);
CREATE INDEX idx_evento_criador_ativo   ON evento_calendario(fk_criador_id, ativo);
CREATE INDEX idx_frequencia_data        ON frequencia(data_aula);
CREATE INDEX idx_frequencia_usuario_mat ON frequencia(fk_usuario_id, fk_materia_id);
CREATE INDEX idx_mensagem_data          ON mensagem(data_publicacao);
CREATE INDEX idx_mensagem_remetente_data ON mensagem(fk_remetente_id, data_publicacao);


-- ================================================================
-- STORED PROCEDURES
-- ================================================================

DELIMITER $$

-- ----------------------------------------------------------------
-- sp_desativar_usuario
-- Soft-delete em cascata lógico.
-- Uso no backend (gestao_usuarios.py):
--   cursor.execute("CALL sp_desativar_usuario(%s)", (id,))
-- ----------------------------------------------------------------
CREATE PROCEDURE sp_desativar_usuario(IN p_usuario_id INT)
BEGIN
    UPDATE usuario          SET ativo = 0 WHERE id             = p_usuario_id;
    UPDATE evento_calendario SET ativo = 0 WHERE fk_criador_id = p_usuario_id AND pessoal = 1;
    UPDATE mensagem          SET ativo = 0 WHERE fk_remetente_id = p_usuario_id;
END$$

-- ----------------------------------------------------------------
-- sp_desativar_turma
-- Soft-delete em cascata lógico.
-- Uso no backend (turmas.py):
--   cursor.execute("CALL sp_desativar_turma(%s)", (turma_id,))
-- ----------------------------------------------------------------
CREATE PROCEDURE sp_desativar_turma(IN p_turma_id INT)
BEGIN
    UPDATE turma             SET ativo = 0 WHERE id          = p_turma_id;
    UPDATE evento_calendario SET ativo = 0 WHERE fk_turma_id = p_turma_id;
    UPDATE mensagem          SET ativo = 0 WHERE fk_turma_id = p_turma_id;
END$$

DELIMITER ;


-- ================================================================
-- Restaurar configurações originais
-- ================================================================
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;

-- ================================================================
-- Dump gerado em 2026-06-08
-- ================================================================