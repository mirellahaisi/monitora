from flask import Blueprint, jsonify, render_template, request
import mysql.connector

from conexao import criar_conexao
from gerador_token import gerar_token, TEMPO_SESSAO


login_bp = Blueprint("login", __name__)


@login_bp.get("/")
def tela_login():
    return render_template("pages/autentificacao.html")


@login_bp.get("/inicio")
def tela_inicio():
    return render_template("pages/inicio.html")


@login_bp.post("/api/login")
def login():
    dados = request.get_json(silent=True) or {}

    email = str(dados.get("email", "")).strip().lower()
    senha = str(dados.get("senha", "")).strip()

    if not email or not senha:
        return jsonify({
            "message": "Informe e-mail e senha."
        }), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT 
                usuario.id,
                usuario.nome,
                usuario.email,
                papel.descricao AS papel
            FROM usuario
            INNER JOIN papel 
                ON papel.id = usuario.fk_papel_id
            WHERE usuario.email = %s
              AND usuario.senha = %s
              AND usuario.ativo = 1
            LIMIT 1
            """,
            (email, senha)
        )

        usuario = cursor.fetchone()

    except mysql.connector.Error as erro:
        print("Erro no banco:", erro)

        return jsonify({
            "message": "Erro ao conectar com o banco de dados.",
            "erro": str(erro)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexao and conexao.is_connected():
            conexao.close()

    if not usuario:
        return jsonify({
            "message": "E-mail ou senha inválidos."
        }), 401

    token, payload = gerar_token(usuario)

    return jsonify({
        "message": "Login realizado com sucesso.",
        "token": token,
        "tempoSessao": TEMPO_SESSAO,
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "papel": usuario["papel"]
        },
        "sessao": {
            "inicio": payload["iat"],
            "expiracao": payload["exp"]
        }
    }), 200