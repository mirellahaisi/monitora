from flask import Blueprint, jsonify, render_template, request
import mysql.connector

from .conexao import criar_conexao
from .login import token_obrigatorio, papel_obrigatorio

cursos_bp = Blueprint("cursos", __name__)


def normalizar_ativo(valor, padrao=False):
    if valor is None:
        return padrao
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, (bytes, bytearray)):
        return any(valor)

    try:
        return int(valor) != 0
    except (TypeError, ValueError):
        texto = str(valor).strip().lower()
        if texto in {"1", "true", "sim", "yes", "ativo", "on"}:
            return True
        if texto in {"0", "false", "nao", "não", "no", "inativo", "off", ""}:
            return False
        return bool(valor)


# ─────────────────────────────────────────────
# PÁGINA HTML
# ─────────────────────────────────────────────

@cursos_bp.get("/cursos")
def tela_cursos():
    return render_template("pages/cursos.html", active_page="cursos")


# ─────────────────────────────────────────────
# LISTAR TODOS OS CURSOS
# ─────────────────────────────────────────────

@cursos_bp.get("/api/cursos")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def listar_cursos(usuario):
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                nome,
                codigo_prefixo,
                ativo,
                data_criacao,
                data_atualizacao
            FROM curso
            ORDER BY nome
        """)

        cursos = cursor.fetchall()

        # Converte campos datetime para string (JSON-serializable)
        for c in cursos:
            if c.get("data_criacao"):
                c["data_criacao"] = c["data_criacao"].strftime("%Y-%m-%d %H:%M:%S")
            if c.get("data_atualizacao"):
                c["data_atualizacao"] = c["data_atualizacao"].strftime("%Y-%m-%d %H:%M:%S")
            c["ativo"] = normalizar_ativo(c.get("ativo"))

        return jsonify({"cursos": cursos}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar cursos.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


# ─────────────────────────────────────────────
# CRIAR CURSO
# ─────────────────────────────────────────────

@cursos_bp.post("/api/cursos")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def criar_curso(usuario):
    dados = request.get_json(silent=True) or {}

    nome            = str(dados.get("nome", "")).strip()
    codigo_prefixo  = str(dados.get("codigo_prefixo", "")).strip().upper()
    ativo           = normalizar_ativo(dados.get("ativo", True), padrao=True)

    # ── Validações ──
    erros = []

    if not nome or len(nome) < 3:
        erros.append("O nome do curso deve ter pelo menos 3 caracteres.")

    if not codigo_prefixo or len(codigo_prefixo) < 2:
        erros.append("O prefixo deve ter pelo menos 2 caracteres.")

    if erros:
        return jsonify({"message": " | ".join(erros)}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        # Verifica duplicidade de nome
        cursor.execute(
            "SELECT id FROM curso WHERE LOWER(nome) = LOWER(%s) LIMIT 1",
            (nome,)
        )
        if cursor.fetchone():
            return jsonify({"message": "Já existe um curso com esse nome."}), 409

        # Verifica duplicidade de prefixo
        cursor.execute(
            "SELECT id FROM curso WHERE UPPER(codigo_prefixo) = %s LIMIT 1",
            (codigo_prefixo,)
        )
        if cursor.fetchone():
            return jsonify({"message": "Já existe um curso com esse prefixo."}), 409

        cursor.execute(
            """
            INSERT INTO curso (nome, codigo_prefixo, ativo)
            VALUES (%s, %s, %s)
            """,
            (nome, codigo_prefixo, ativo)
        )
        conexao.commit()
        novo_id = cursor.lastrowid

        return jsonify({
            "message": "Curso cadastrado com sucesso.",
            "id": novo_id
        }), 201

    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()
        return jsonify({"message": "Erro ao cadastrar curso.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


# ─────────────────────────────────────────────
# ATUALIZAR CURSO
# ─────────────────────────────────────────────

@cursos_bp.put("/api/cursos/<int:curso_id>")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def atualizar_curso(usuario, curso_id):
    dados = request.get_json(silent=True) or {}

    nome            = str(dados.get("nome", "")).strip()
    codigo_prefixo  = str(dados.get("codigo_prefixo", "")).strip().upper()
    ativo           = normalizar_ativo(dados.get("ativo", True), padrao=True)

    # ── Validações ──
    erros = []

    if not nome or len(nome) < 3:
        erros.append("O nome do curso deve ter pelo menos 3 caracteres.")

    if not codigo_prefixo or len(codigo_prefixo) < 2:
        erros.append("O prefixo deve ter pelo menos 2 caracteres.")

    if erros:
        return jsonify({"message": " | ".join(erros)}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        # Verifica se o curso existe
        cursor.execute("SELECT id FROM curso WHERE id = %s LIMIT 1", (curso_id,))
        if not cursor.fetchone():
            return jsonify({"message": "Curso não encontrado."}), 404

        # Verifica duplicidade de nome (excluindo o próprio registro)
        cursor.execute(
            "SELECT id FROM curso WHERE LOWER(nome) = LOWER(%s) AND id != %s LIMIT 1",
            (nome, curso_id)
        )
        if cursor.fetchone():
            return jsonify({"message": "Já existe outro curso com esse nome."}), 409

        # Verifica duplicidade de prefixo
        cursor.execute(
            "SELECT id FROM curso WHERE UPPER(codigo_prefixo) = %s AND id != %s LIMIT 1",
            (codigo_prefixo, curso_id)
        )
        if cursor.fetchone():
            return jsonify({"message": "Já existe outro curso com esse prefixo."}), 409

        cursor.execute(
            """
            UPDATE curso
            SET nome = %s,
                codigo_prefixo = %s,
                ativo = %s
            WHERE id = %s
            """,
            (nome, codigo_prefixo, ativo, curso_id)
        )
        conexao.commit()

        return jsonify({"message": "Curso atualizado com sucesso."}), 200

    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()
        return jsonify({"message": "Erro ao atualizar curso.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


# ─────────────────────────────────────────────
# EXCLUIR CURSO
# ─────────────────────────────────────────────

@cursos_bp.delete("/api/cursos/<int:curso_id>")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def excluir_curso(usuario, curso_id):
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        # Verifica se o curso existe
        cursor.execute("SELECT id, nome FROM curso WHERE id = %s LIMIT 1", (curso_id,))
        curso = cursor.fetchone()
        if not curso:
            return jsonify({"message": "Curso não encontrado."}), 404

        # Verifica se há turmas vinculadas ao curso
        cursor.execute(
            "SELECT COUNT(*) AS total FROM turma WHERE fk_curso_id = %s AND ativo = 1",
            (curso_id,)
        )
        row = cursor.fetchone()
        if row and row["total"] > 0:
            return jsonify({
                "message": f"Não é possível excluir: existem {row['total']} turma(s) ativa(s) vinculada(s) a este curso."
            }), 409

        cursor.execute("DELETE FROM curso WHERE id = %s", (curso_id,))
        conexao.commit()

        return jsonify({"message": "Curso excluído com sucesso."}), 200

    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()
        return jsonify({"message": "Erro ao excluir curso.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()
