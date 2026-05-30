from flask import Blueprint, jsonify, render_template, request
import mysql.connector

from conexao import criar_conexao
from login import token_obrigatorio, papel_obrigatorio

turmas_bp = Blueprint("turmas", __name__)


# ========================
# ROTA DE TELA
# ========================

@turmas_bp.get("/turmas")
def tela_turmas():
    return render_template("pages/turmas.html", active_page="turmas")


# ========================
# APIS
# ========================

@turmas_bp.get("/api/turmas")
@token_obrigatorio
def listar_turmas(usuario):
    """
    Professor  → apenas as turmas em que leciona.
    Coordenador/Admin → todas as turmas ativas.
    """
    papel = str(usuario.get("papel", "")).lower()
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        if papel == "professor":
            cursor.execute("""
                SELECT
                    t.id,
                    t.nome,
                    t.codigo,
                    t.periodo,
                    t.turno,
                    t.ano,
                    t.semestre,
                    t.capacidade,
                    COUNT(DISTINCT ut.fk_usuario_id) AS total_alunos,
                    GROUP_CONCAT(DISTINCT m.nome ORDER BY m.nome SEPARATOR ', ') AS materias
                FROM turma t
                INNER JOIN materias_turma mt ON mt.fk_turma_id = t.id
                INNER JOIN professor_materia pm ON pm.fk_materia_id = mt.fk_materia_id
                LEFT JOIN usuario_turma ut ON ut.fk_turma_id = t.id
                LEFT JOIN materia m ON m.id = mt.fk_materia_id AND m.ativo = 1
                WHERE pm.fk_usuario_id = %s AND t.ativo = 1
                GROUP BY t.id, t.nome, t.codigo, t.periodo, t.turno, t.ano, t.semestre, t.capacidade
                ORDER BY t.periodo, t.nome
            """, (usuario["id"],))
        else:
            cursor.execute("""
                SELECT
                    t.id,
                    t.nome,
                    t.codigo,
                    t.periodo,
                    t.turno,
                    t.ano,
                    t.semestre,
                    t.capacidade,
                    COUNT(DISTINCT ut.fk_usuario_id) AS total_alunos,
                    GROUP_CONCAT(DISTINCT m.nome ORDER BY m.nome SEPARATOR ', ') AS materias
                FROM turma t
                LEFT JOIN materias_turma mt ON mt.fk_turma_id = t.id
                LEFT JOIN usuario_turma ut ON ut.fk_turma_id = t.id
                LEFT JOIN materia m ON m.id = mt.fk_materia_id AND m.ativo = 1
                WHERE t.ativo = 1
                GROUP BY t.id, t.nome, t.codigo, t.periodo, t.turno, t.ano, t.semestre, t.capacidade
                ORDER BY t.periodo, t.nome
            """)

        turmas = cursor.fetchall()
        return jsonify({"turmas": turmas}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar turmas.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.get("/api/minha-turma")
@token_obrigatorio
def minha_turma(usuario):
    """
    Aluno → retorna sua turma e a lista de colegas em ordem alfabética.
    """
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        # Busca a turma do aluno logado
        cursor.execute("""
            SELECT
                t.id,
                t.nome,
                t.codigo,
                t.periodo,
                t.turno,
                t.ano,
                t.semestre,
                t.capacidade,
                COUNT(DISTINCT ut2.fk_usuario_id) AS total_alunos,
                GROUP_CONCAT(DISTINCT m.nome ORDER BY m.nome SEPARATOR ', ') AS materias
            FROM turma t
            INNER JOIN usuario_turma ut ON ut.fk_turma_id = t.id AND ut.fk_usuario_id = %s
            LEFT JOIN usuario_turma ut2 ON ut2.fk_turma_id = t.id
            LEFT JOIN materias_turma mt ON mt.fk_turma_id = t.id
            LEFT JOIN materia m ON m.id = mt.fk_materia_id AND m.ativo = 1
            WHERE t.ativo = 1
            GROUP BY t.id, t.nome, t.codigo, t.periodo, t.turno, t.ano, t.semestre, t.capacidade
            LIMIT 1
        """, (usuario["id"],))

        turma = cursor.fetchone()
        if not turma:
            return jsonify({"message": "Você não está matriculado em nenhuma turma ativa."}), 404

        # Busca os colegas da turma em ordem alfabética
        cursor.execute("""
            SELECT
                u.id,
                u.nome,
                u.email
            FROM usuario u
            INNER JOIN usuario_turma ut ON ut.fk_usuario_id = u.id
            INNER JOIN papel p ON p.id = u.fk_papel_id
            WHERE ut.fk_turma_id = %s
              AND LOWER(p.descricao) = 'aluno'
              AND u.ativo = 1
            ORDER BY u.nome ASC
        """, (turma["id"],))

        alunos = cursor.fetchall()
        return jsonify({"turma": turma, "alunos": alunos}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar sua turma.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.get("/api/turmas/<int:turma_id>/alunos")
@token_obrigatorio
def listar_alunos_turma(usuario, turma_id):
    """Retorna alunos matriculados numa turma com médias gerais."""
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                u.id,
                u.nome,
                u.email,
                ROUND(AVG(n.valor), 2) AS media_geral,
                COUNT(DISTINCT n.fk_materia_id) AS materias_com_nota
            FROM usuario u
            INNER JOIN usuario_turma ut ON ut.fk_usuario_id = u.id
            INNER JOIN papel p ON p.id = u.fk_papel_id
            LEFT JOIN nota n ON n.fk_usuario_id = u.id
            WHERE ut.fk_turma_id = %s
              AND LOWER(p.descricao) = 'aluno'
              AND u.ativo = 1
            GROUP BY u.id, u.nome, u.email
            ORDER BY u.nome
        """, (turma_id,))

        alunos = cursor.fetchall()

        for a in alunos:
            if a["media_geral"] is not None:
                a["media_geral"] = float(a["media_geral"])

        return jsonify({"alunos": alunos}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar alunos.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.get("/api/turmas/<int:turma_id>/materias")
@token_obrigatorio
def listar_materias_turma(usuario, turma_id):
    """Retorna matérias de uma turma com professor responsável."""
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                m.id,
                m.nome,
                m.carga_horaria,
                GROUP_CONCAT(DISTINCT u.nome ORDER BY u.nome SEPARATOR ', ') AS professores
            FROM materia m
            INNER JOIN materias_turma mt ON mt.fk_materia_id = m.id
            LEFT JOIN professor_materia pm ON pm.fk_materia_id = m.id
            LEFT JOIN usuario u ON u.id = pm.fk_usuario_id AND u.ativo = 1
            WHERE mt.fk_turma_id = %s AND m.ativo = 1
            GROUP BY m.id, m.nome, m.carga_horaria
            ORDER BY m.nome
        """, (turma_id,))

        materias = cursor.fetchall()
        return jsonify({"materias": materias}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar matérias.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.post("/api/turmas")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def criar_turma(usuario):
    dados = request.get_json(silent=True) or {}

    campos_obrigatorios = ["nome", "codigo", "periodo", "turno", "ano", "semestre", "capacidade"]
    for campo in campos_obrigatorios:
        if not dados.get(campo):
            return jsonify({"message": f"Campo '{campo}' é obrigatório."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO turma (nome, codigo, periodo, turno, ano, semestre, capacidade, ativo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
        """, (
            dados["nome"],
            dados["codigo"],
            dados["periodo"],
            dados["turno"],
            dados["ano"],
            dados["semestre"],
            dados["capacidade"],
        ))

        conexao.commit()
        return jsonify({"message": "Turma criada com sucesso.", "id": cursor.lastrowid}), 201

    except mysql.connector.Error as erro:
        if "Duplicate entry" in str(erro):
            return jsonify({"message": "Já existe uma turma com esse código."}), 409
        return jsonify({"message": "Erro ao criar turma.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.delete("/api/turmas/<int:turma_id>")
@token_obrigatorio
@papel_obrigatorio("admin", "adm")
def desativar_turma(usuario, turma_id):
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()

        cursor.execute("UPDATE turma SET ativo = 0 WHERE id = %s AND ativo = 1", (turma_id,))
        conexao.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Turma não encontrada."}), 404

        return jsonify({"message": "Turma removida com sucesso."}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao remover turma.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()