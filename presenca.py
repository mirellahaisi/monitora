from flask import Blueprint, render_template, request, jsonify
import mysql.connector

from conexao import criar_conexao
from login import token_obrigatorio, papel_obrigatorio

presenca_bp = Blueprint("presenca", __name__)


@presenca_bp.get("/presenca")
def tela_presenca():
    return render_template("pages/presenca.html", active_page="presenca")


@presenca_bp.get("/api/presenca/materias")
@token_obrigatorio
@papel_obrigatorio("professor")
def listar_materias_professor(usuario):
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT m.id, m.nome
            FROM materia m
            INNER JOIN professor_materia pm
                ON pm.fk_materia_id = m.id
            WHERE pm.fk_usuario_id = %s
              AND m.ativo = 1
            ORDER BY m.nome
        """, (usuario["id"],))

        return jsonify({"materias": cursor.fetchall()}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar matérias.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@presenca_bp.get("/api/presenca/turmas")
@token_obrigatorio
@papel_obrigatorio("professor")
def listar_turmas_por_materia(usuario):
    materia_id = request.args.get("materia_id")

    if not materia_id:
        return jsonify({"message": "Informe a matéria."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT t.id, t.nome, t.periodo
            FROM turma t
            INNER JOIN materias_turma mt
                ON mt.fk_turma_id = t.id
            INNER JOIN professor_materia pm
                ON pm.fk_materia_id = mt.fk_materia_id
            WHERE pm.fk_usuario_id = %s
              AND mt.fk_materia_id = %s
              AND t.ativo = 1
            ORDER BY t.nome
        """, (usuario["id"], materia_id))

        return jsonify({"turmas": cursor.fetchall()}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar turmas.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@presenca_bp.get("/api/presenca/alunos")
@token_obrigatorio
@papel_obrigatorio("professor")
def listar_alunos_presenca(usuario):
    materia_id = request.args.get("materia_id")
    turma_id = request.args.get("turma_id")
    data_aula = request.args.get("data_aula")

    if not materia_id or not turma_id or not data_aula:
        return jsonify({"message": "Informe matéria, turma e data."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                u.id,
                u.nome,
                f.presente,
                f.justificativa
            FROM usuario u
            INNER JOIN usuario_turma ut
                ON ut.fk_usuario_id = u.id
            INNER JOIN papel p
                ON p.id = u.fk_papel_id
            LEFT JOIN frequencia f
                ON f.fk_usuario_id = u.id
               AND f.fk_materia_id = %s
               AND f.data_aula = %s
            WHERE ut.fk_turma_id = %s
              AND LOWER(p.descricao) = 'aluno'
              AND u.ativo = 1
            ORDER BY u.nome
        """, (materia_id, data_aula, turma_id))

        return jsonify({"alunos": cursor.fetchall()}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar alunos.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@presenca_bp.post("/api/presenca/salvar")
@token_obrigatorio
@papel_obrigatorio("professor")
def salvar_presenca(usuario):
    dados = request.get_json(silent=True) or {}

    materia_id = dados.get("materia_id")
    turma_id = dados.get("turma_id")
    data_aula = dados.get("data_aula")
    justificativa = dados.get("justificativa")
    alunos = dados.get("alunos", [])

    if not materia_id or not turma_id or not data_aula or not alunos:
        return jsonify({"message": "Preencha matéria, turma, data e presença dos alunos."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT 1
            FROM professor_materia pm
            INNER JOIN materias_turma mt
                ON mt.fk_materia_id = pm.fk_materia_id
            WHERE pm.fk_usuario_id = %s
              AND pm.fk_materia_id = %s
              AND mt.fk_turma_id = %s
            LIMIT 1
        """, (usuario["id"], materia_id, turma_id))

        permitido = cursor.fetchone()

        if not permitido:
            return jsonify({
                "message": "Você não tem permissão para lançar presença nessa turma/matéria."
            }), 403

        for aluno in alunos:
            aluno_id = aluno.get("aluno_id")
            presente = aluno.get("presente")

            cursor.execute("""
                SELECT id
                FROM frequencia
                WHERE fk_usuario_id = %s
                  AND fk_materia_id = %s
                  AND data_aula = %s
                LIMIT 1
            """, (aluno_id, materia_id, data_aula))

            registro = cursor.fetchone()

            if registro:
                cursor.execute("""
                    UPDATE frequencia
                    SET presente = %s,
                        justificativa = %s,
                        data_atualizacao = NOW()
                    WHERE id = %s
                """, (presente, justificativa, registro["id"]))
            else:
                cursor.execute("""
                    INSERT INTO frequencia (
                        data_aula,
                        presente,
                        justificativa,
                        data_criacao,
                        data_atualizacao,
                        fk_usuario_id,
                        fk_materia_id
                    ) VALUES (%s, %s, %s, NOW(), NOW(), %s, %s)
                """, (data_aula, presente, justificativa, aluno_id, materia_id))

        conexao.commit()

        return jsonify({"message": "Presença salva com sucesso."}), 200

    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()

        return jsonify({"message": "Erro ao salvar presença.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()