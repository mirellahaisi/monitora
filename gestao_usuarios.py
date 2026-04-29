from flask import Blueprint, jsonify, render_template, request
import mysql.connector

from conexao import criar_conexao
from login import token_obrigatorio, papel_obrigatorio


gestao_usuarios_bp = Blueprint("gestao_usuarios", __name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _listar_usuarios_por_papel(papeis: list):
    """Retorna (lista, erro) filtrando usuario por papel.descricao."""
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        placeholders = ", ".join(["%s"] * len(papeis))

        cursor.execute(
            f"""
            SELECT
                usuario.id,
                usuario.nome,
                usuario.cpf,
                usuario.email,
                usuario.telefone,
                usuario.data_nascimento,
                usuario.especialidade,
                usuario.salario,
                usuario.data_criacao,
                papel.descricao AS papel
            FROM usuario
            INNER JOIN papel
                ON papel.id = usuario.fk_papel_id
            WHERE LOWER(papel.descricao) IN ({placeholders})
              AND usuario.ativo = 1
            ORDER BY usuario.nome ASC
            """,
            [p.lower() for p in papeis]
        )

        usuarios = cursor.fetchall()

        for u in usuarios:
            if u.get("data_nascimento"):
                u["data_nascimento"] = u["data_nascimento"].strftime("%Y-%m-%d")
            if u.get("data_criacao"):
                u["data_criacao"] = u["data_criacao"].strftime("%Y-%m-%d %H:%M:%S")
            if u.get("salario") is not None:
                u["salario"] = float(u["salario"])

        return usuarios, None

    except mysql.connector.Error as erro:
        print("Erro no banco:", erro)
        return None, str(erro)

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


# ── Rotas ─────────────────────────────────────────────────────────────────────

@gestao_usuarios_bp.get("/gestao-usuarios")
def tela_gestao_usuarios():
    return render_template("pages/gestao_usuarios.html")


@gestao_usuarios_bp.get("/api/usuarios/alunos")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def listar_alunos(usuario):
    usuarios, erro = _listar_usuarios_por_papel(["aluno"])

    if erro:
        return jsonify({"message": "Erro ao buscar alunos.", "erro": erro}), 500

    return jsonify({"usuarios": usuarios}), 200


@gestao_usuarios_bp.get("/api/usuarios/coordenacao")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def listar_coordenacao(usuario):
    usuarios, erro = _listar_usuarios_por_papel(["admin", "adm", "coordenador"])

    if erro:
        return jsonify({"message": "Erro ao buscar coordenação.", "erro": erro}), 500

    return jsonify({"usuarios": usuarios}), 200


@gestao_usuarios_bp.get("/api/usuarios/professores")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def listar_professores(usuario):
    usuarios, erro = _listar_usuarios_por_papel(["professor"])

    if erro:
        return jsonify({"message": "Erro ao buscar professores.", "erro": erro}), 500

    return jsonify({"usuarios": usuarios}), 200



# CHATE -------------------------------------------------------

def _criar_usuario_com_papel(dados, fk_papel_id):
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO usuario (
                nome, cpf, email, telefone,
                data_nascimento, especialidade,
                salario, fk_papel_id, ativo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
        """, (
            dados.get("nome"),
            dados.get("cpf"),
            dados.get("email"),
            dados.get("telefone"),
            dados.get("data_nascimento"),
            dados.get("especialidade"),
            dados.get("salario"),
            fk_papel_id
        ))

        conexao.commit()
        return None

    except mysql.connector.Error as erro:
        return str(erro)

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()

@gestao_usuarios_bp.post("/api/usuarios/alunos")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def criar_aluno(usuario_logado):
    dados = request.json

    erro = _criar_usuario_com_papel(dados, 3)

    if erro:
        return jsonify({"message": "Erro ao criar aluno.", "erro": erro}), 500

    return jsonify({"message": "Aluno criado com sucesso."}), 201

@gestao_usuarios_bp.post("/api/usuarios/professores")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def criar_professor(usuario_logado):
    dados = request.json

    erro = _criar_usuario_com_papel(dados, 2)

    if erro:
        return jsonify({"message": "Erro ao criar professor.", "erro": erro}), 500

    return jsonify({"message": "Professor criado com sucesso."}), 201

@gestao_usuarios_bp.post("/api/usuarios/coordenacao")
@token_obrigatorio
@papel_obrigatorio("admin", "adm")
def criar_coordenador(usuario_logado):
    dados = request.json

    erro = _criar_usuario_com_papel(dados, 1)

    if erro:
        return jsonify({"message": "Erro ao criar coordenador.", "erro": erro}), 500

    return jsonify({"message": "Coordenador criado com sucesso."}), 201

@gestao_usuarios_bp.put("/api/usuarios/<int:id>")
@token_obrigatorio
@papel_obrigatorio("admin", "adm")
def atualizar_usuario(usuario_logado, id):
    dados = request.json

    campos = []
    valores = []

    for campo in ["nome", "cpf", "email", "telefone", "data_nascimento", "especialidade", "salario"]:
        if campo in dados:
            campos.append(f"{campo} = %s")
            valores.append(dados[campo])

    if not campos:
        return jsonify({"message": "Nenhum campo para atualizar."}), 400

    valores.append(id)

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()

        cursor.execute(f"""
            UPDATE usuario
            SET {", ".join(campos)}
            WHERE id = %s AND ativo = 1
        """, valores)

        conexao.commit()

        return jsonify({"message": "Usuário atualizado com sucesso."}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao atualizar usuário.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()

@gestao_usuarios_bp.delete("/api/usuarios/<int:id>")
@token_obrigatorio
@papel_obrigatorio("admin", "adm")
def deletar_usuario(usuario_logado, id):
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()

        cursor.execute(
            "UPDATE usuario SET ativo = 0 WHERE id = %s AND ativo = 1",
            (id,)
        )
        conexao.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Usuário não encontrado."}), 404

        return jsonify({"message": "Usuário removido com sucesso."}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao remover usuário.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()

@gestao_usuarios_bp.get("/api/usuarios/<int:id>")
@token_obrigatorio
def buscar_usuario(usuario_logado, id):
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT u.id, u.nome, u.cpf, u.email, u.telefone,
                u.data_nascimento, u.especialidade, u.salario,
                p.descricao AS papel
            FROM usuario u
            INNER JOIN papel p ON p.id = u.fk_papel_id
            WHERE u.id = %s AND u.ativo = 1
        """, (id,))

        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({"message": "Usuário não encontrado."}), 404

        if usuario.get("data_nascimento"):
            usuario["data_nascimento"] = usuario["data_nascimento"].strftime("%Y-%m-%d")
        if usuario.get("salario") is not None:
            usuario["salario"] = float(usuario["salario"])

        return jsonify({"usuario": usuario}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar usuário.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()