from flask import Blueprint, jsonify, render_template, request
import mysql.connector

from conexao import criar_conexao
from login import token_obrigatorio, papel_obrigatorio

materias_bp = Blueprint("materias", __name__)


# ─────────────────────────────────────────────
# PÁGINA HTML
# ─────────────────────────────────────────────

@materias_bp.get("/materias")
def tela_materias():
    return render_template("pages/materias.html", active_page="materias")


# ─────────────────────────────────────────────
# LISTAR TODAS AS MATÉRIAS
# ─────────────────────────────────────────────

@materias_bp.get("/api/materias")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def listar_materias(usuario):
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                nome,
                codigo,
                carga_horaria,
                descricao,
                ativo,
                data_criacao,
                data_atualizacao
            FROM materia
            ORDER BY nome
        """)

        materias = cursor.fetchall()

        for m in materias:
            if m.get("data_criacao"):
                m["data_criacao"] = m["data_criacao"].strftime("%Y-%m-%d %H:%M:%S")
            if m.get("data_atualizacao"):
                m["data_atualizacao"] = m["data_atualizacao"].strftime("%Y-%m-%d %H:%M:%S")
            m["ativo"] = bool(int(m["ativo"]) if m["ativo"] is not None else 0)
            m["carga_horaria"] = int(m["carga_horaria"]) if m["carga_horaria"] else None

        return jsonify({"materias": materias}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar matérias.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


# ─────────────────────────────────────────────
# CRIAR MATÉRIA
# ─────────────────────────────────────────────

@materias_bp.post("/api/materias")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def criar_materia(usuario):
    dados = request.get_json(silent=True) or {}

    nome          = str(dados.get("nome", "")).strip()
    codigo        = str(dados.get("codigo", "")).strip().upper()
    carga_horaria = dados.get("carga_horaria")
    descricao     = str(dados.get("descricao", "") or "").strip() or None
    ativo         = bool(dados.get("ativo", True))

    # ── Validações ──
    erros = []

    if not nome or len(nome) < 3:
        erros.append("O nome da matéria deve ter pelo menos 3 caracteres.")

    if not codigo or len(codigo) < 2:
        erros.append("O código deve ter pelo menos 2 caracteres.")

    try:
        carga_horaria = int(carga_horaria)
        if carga_horaria < 1:
            raise ValueError
    except (TypeError, ValueError):
        erros.append("Informe uma carga horária válida (mínimo 1 hora).")

    if erros:
        return jsonify({"message": " | ".join(erros)}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        # Verifica duplicidade de nome
        cursor.execute(
            "SELECT id FROM materia WHERE LOWER(nome) = LOWER(%s) LIMIT 1",
            (nome,)
        )
        if cursor.fetchone():
            return jsonify({"message": "Já existe uma matéria com esse nome."}), 409

        # Verifica duplicidade de código
        cursor.execute(
            "SELECT id FROM materia WHERE UPPER(codigo) = %s LIMIT 1",
            (codigo,)
        )
        if cursor.fetchone():
            return jsonify({"message": "Já existe uma matéria com esse código."}), 409

        cursor.execute(
            """
            INSERT INTO materia (nome, codigo, carga_horaria, descricao, ativo)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (nome, codigo, carga_horaria, descricao, ativo)
        )
        conexao.commit()
        novo_id = cursor.lastrowid

        return jsonify({
            "message": "Matéria cadastrada com sucesso.",
            "id": novo_id
        }), 201

    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()
        return jsonify({"message": "Erro ao cadastrar matéria.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


# ─────────────────────────────────────────────
# ATUALIZAR MATÉRIA
# ─────────────────────────────────────────────

@materias_bp.put("/api/materias/<int:materia_id>")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def atualizar_materia(usuario, materia_id):
    dados = request.get_json(silent=True) or {}

    nome          = str(dados.get("nome", "")).strip()
    codigo        = str(dados.get("codigo", "")).strip().upper()
    carga_horaria = dados.get("carga_horaria")
    descricao     = str(dados.get("descricao", "") or "").strip() or None
    ativo         = bool(dados.get("ativo", True))

    # ── Validações ──
    erros = []

    if not nome or len(nome) < 3:
        erros.append("O nome da matéria deve ter pelo menos 3 caracteres.")

    if not codigo or len(codigo) < 2:
        erros.append("O código deve ter pelo menos 2 caracteres.")

    try:
        carga_horaria = int(carga_horaria)
        if carga_horaria < 1:
            raise ValueError
    except (TypeError, ValueError):
        erros.append("Informe uma carga horária válida (mínimo 1 hora).")

    if erros:
        return jsonify({"message": " | ".join(erros)}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        # Verifica se a matéria existe
        cursor.execute("SELECT id FROM materia WHERE id = %s LIMIT 1", (materia_id,))
        if not cursor.fetchone():
            return jsonify({"message": "Matéria não encontrada."}), 404

        # Verifica duplicidade de nome (excluindo o próprio registro)
        cursor.execute(
            "SELECT id FROM materia WHERE LOWER(nome) = LOWER(%s) AND id != %s LIMIT 1",
            (nome, materia_id)
        )
        if cursor.fetchone():
            return jsonify({"message": "Já existe outra matéria com esse nome."}), 409

        # Verifica duplicidade de código
        cursor.execute(
            "SELECT id FROM materia WHERE UPPER(codigo) = %s AND id != %s LIMIT 1",
            (codigo, materia_id)
        )
        if cursor.fetchone():
            return jsonify({"message": "Já existe outra matéria com esse código."}), 409

        cursor.execute(
            """
            UPDATE materia
            SET nome          = %s,
                codigo        = %s,
                carga_horaria = %s,
                descricao     = %s,
                ativo         = %s
            WHERE id = %s
            """,
            (nome, codigo, carga_horaria, descricao, ativo, materia_id)
        )
        conexao.commit()

        return jsonify({"message": "Matéria atualizada com sucesso."}), 200

    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()
        return jsonify({"message": "Erro ao atualizar matéria.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


# ─────────────────────────────────────────────
# EXCLUIR MATÉRIA
# ─────────────────────────────────────────────

@materias_bp.delete("/api/materias/<int:materia_id>")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def excluir_materia(usuario, materia_id):
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        # Verifica se a matéria existe
        cursor.execute("SELECT id, nome FROM materia WHERE id = %s LIMIT 1", (materia_id,))
        materia = cursor.fetchone()
        if not materia:
            return jsonify({"message": "Matéria não encontrada."}), 404

        # Verifica se há notas vinculadas
        cursor.execute(
            "SELECT COUNT(*) AS total FROM nota WHERE fk_materia_id = %s",
            (materia_id,)
        )
        row = cursor.fetchone()
        if row and row["total"] > 0:
            return jsonify({
                "message": f"Não é possível excluir: existem {row['total']} nota(s) registrada(s) para esta matéria."
            }), 409

        # Verifica se há turmas vinculadas
        cursor.execute(
            "SELECT COUNT(*) AS total FROM materias_turma WHERE fk_materia_id = %s",
            (materia_id,)
        )
        row = cursor.fetchone()
        if row and row["total"] > 0:
            return jsonify({
                "message": f"Não é possível excluir: a matéria está vinculada a {row['total']} turma(s)."
            }), 409

        cursor.execute("DELETE FROM materia WHERE id = %s", (materia_id,))
        conexao.commit()

        return jsonify({"message": "Matéria excluída com sucesso."}), 200

    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()
        return jsonify({"message": "Erro ao excluir matéria.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()