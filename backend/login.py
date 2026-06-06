from datetime import date, datetime
from functools import wraps
import re

from flask import Blueprint, jsonify, render_template, request
import mysql.connector

from .conexao import criar_conexao
from .gerador_token import gerar_token, validar_token, TEMPO_SESSAO
from .seguranca import (
    gerar_hash_senha,
    senha_padrao_data_nascimento,
    senha_precisa_upgrade,
    verificar_senha,
)


login_bp = Blueprint("login", __name__)


def somente_numeros(valor):
    return "".join(filter(str.isdigit, str(valor or "")))


EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def email_valido(email):
    return bool(EMAIL_REGEX.match(str(email or "").strip()))


def converter_data_iso(valor):
    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    texto = str(valor or "").strip()
    if not texto:
        return None

    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except ValueError:
        return None


def idade_minima_valida(data_nascimento, idade_minima=12):
    if not data_nascimento:
        return False

    hoje = date.today()
    idade = hoje.year - data_nascimento.year
    if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1

    return idade >= idade_minima


def obter_token_requisicao():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    return auth_header.replace("Bearer ", "").strip()


def token_obrigatorio(funcao):
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        token = obter_token_requisicao()

        if not token:
            return jsonify({
                "message": "Token não informado."
            }), 401

        usuario = validar_token(token)

        if not usuario:
            return jsonify({
                "message": "Token inválido ou expirado."
            }), 401

        return funcao(usuario, *args, **kwargs)

    return wrapper


def papel_obrigatorio(*papeis_permitidos):
    def decorator(funcao):
        @wraps(funcao)
        def wrapper(usuario, *args, **kwargs):
            papel_usuario = str(usuario.get("papel", "")).lower()

            papeis_normalizados = [
                str(papel).lower() for papel in papeis_permitidos
            ]

            if papel_usuario not in papeis_normalizados:
                return jsonify({
                    "message": "Usuário sem permissão para acessar este recurso."
                }), 403

            return funcao(usuario, *args, **kwargs)

        return wrapper

    return decorator


@login_bp.get("/login")
def tela_login():
    return render_template("pages/autentificacao.html")


@login_bp.get("/inicio")
def tela_inicio():
    return render_template("pages/inicio.html", active_page='inicio')


@login_bp.get("/perfil")
def tela_perfil():
    return render_template("pages/perfil.html", active_page='perfil')


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
                usuario.senha,
                usuario.data_nascimento,
                usuario.fk_papel_id AS fk_papel_id,
                papel.descricao AS papel
            FROM usuario
            INNER JOIN papel 
                ON papel.id = usuario.fk_papel_id
            WHERE usuario.email = %s
              AND usuario.ativo = 1
            LIMIT 1
            """,
            (email,)
        )

        usuario = cursor.fetchone()

        senha_banco = usuario.get("senha") if usuario else None
        senha_valida = verificar_senha(senha, senha_banco) if usuario else False

        if usuario and not senha_valida and not str(senha_banco or "").strip():
            try:
                senha_padrao = senha_padrao_data_nascimento(usuario.get("data_nascimento"))
            except ValueError:
                senha_padrao = None

            if senha_padrao and senha == senha_padrao:
                senha_valida = True
                cursor.execute(
                    "UPDATE usuario SET senha = %s WHERE id = %s",
                    (gerar_hash_senha(senha_padrao), usuario["id"])
                )
                conexao.commit()

        if not usuario or not senha_valida:
            return jsonify({
                "message": "E-mail ou senha invalidos."
            }), 401

        if senha_precisa_upgrade(senha_banco):
            cursor.execute(
                "UPDATE usuario SET senha = %s WHERE id = %s",
                (gerar_hash_senha(senha), usuario["id"])
            )
            conexao.commit()

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
            "papel": usuario["papel"],
            "papel_id": usuario.get("fk_papel_id")
        },
        "sessao": {
            "inicio": payload["iat"],
            "expiracao": payload["exp"]
        }
    }), 200


@login_bp.post("/api/esqueci-senha")
def esqueci_senha():
    dados = request.get_json(silent=True) or {}

    email = str(dados.get("email", "")).strip().lower()
    senha_atual = str(dados.get("senha_atual", "")).strip()
    nova_senha = str(dados.get("nova_senha", "")).strip()

    if not email or not senha_atual or not nova_senha:
        return jsonify({
            "message": "Informe e-mail, senha atual e nova senha."
        }), 400

    if not email_valido(email):
        return jsonify({
            "message": "Informe um e-mail valido."
        }), 400

    if len(nova_senha) < 6:
        return jsonify({
            "message": "A nova senha deve ter pelo menos 6 caracteres."
        }), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, senha
            FROM usuario
            WHERE email = %s
              AND ativo = 1
            LIMIT 1
            """,
            (email,)
        )

        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({
                "message": "E-mail ou senha invalidos."
            }), 401

        if not verificar_senha(senha_atual, usuario.get("senha")):
            return jsonify({
                "message": "A senha atual nao confere."
            }), 403

        if verificar_senha(nova_senha, usuario.get("senha")):
            return jsonify({
                "message": "A nova senha nao pode ser igual a senha atual."
            }), 400

        cursor.execute(
            """
            UPDATE usuario
            SET senha = %s
            WHERE id = %s
            """,
            (gerar_hash_senha(nova_senha), usuario["id"])
        )
        conexao.commit()

        return jsonify({
            "message": "Senha alterada com sucesso."
        }), 200

    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()

        return jsonify({
            "message": "Erro ao alterar a senha.",
            "erro": str(erro)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexao and conexao.is_connected():
            conexao.close()


@login_bp.get("/api/usuario-logado")
@token_obrigatorio
def usuario_logado(usuario):
    return jsonify({
        "logado": True,
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "papel": usuario["papel"],
            "papel_id": usuario.get("papel_id") or usuario.get("fk_papel_id")
        }
    }), 200


@login_bp.get("/api/perfil")
@token_obrigatorio
def buscar_perfil(usuario):
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
                usuario.telefone,
                usuario.cpf,
                usuario.data_nascimento,
                papel.descricao AS papel
            FROM usuario
            INNER JOIN papel
                ON papel.id = usuario.fk_papel_id
            WHERE usuario.id = %s
              AND usuario.ativo = 1
            LIMIT 1
            """,
            (usuario["id"],)
        )

        perfil = cursor.fetchone()

        if not perfil:
            return jsonify({
                "message": "Usuário não encontrado."
            }), 404

        data_nascimento = perfil["data_nascimento"]

        if data_nascimento:
            data_nascimento = data_nascimento.strftime("%Y-%m-%d")

        return jsonify({
            "usuario": {
                "id": perfil["id"],
                "nome": perfil["nome"],
                "email": perfil["email"],
                "telefone": somente_numeros(perfil["telefone"]),
                "cpf": somente_numeros(perfil["cpf"]),
                "data_nascimento": data_nascimento,
                "papel": perfil["papel"]
            }
        }), 200

    except mysql.connector.Error as erro:
        print("Erro no banco:", erro)

        return jsonify({
            "message": "Erro ao buscar dados do perfil.",
            "erro": str(erro)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexao and conexao.is_connected():
            conexao.close()


@login_bp.put("/api/perfil")
@token_obrigatorio
def atualizar_perfil(usuario):
    dados = request.get_json(silent=True) or {}

    nome = str(dados.get("nome", "")).strip()
    email = str(dados.get("email", "")).strip().lower()
    telefone = somente_numeros(dados.get("telefone"))
    data_nascimento = str(dados.get("data_nascimento", "")).strip()
    senha_atual = str(dados.get("senha_atual", "")).strip()
    nova_senha = str(dados.get("nova_senha", "")).strip()

    if not nome or not email or not telefone or not data_nascimento:
        return jsonify({
            "message": "Preencha todos os campos obrigatórios."
        }), 400

    if len(nome) < 3:
        return jsonify({
            "message": "O nome deve ter pelo menos 3 letras."
        }), 400

    if not email_valido(email):
        return jsonify({
            "message": "Digite um e-mail válido."
        }), 400

    data_nascimento_date = converter_data_iso(data_nascimento)
    if not data_nascimento_date:
        return jsonify({
            "message": "Informe uma data de nascimento válida."
        }), 400

    if not idade_minima_valida(data_nascimento_date):
        return jsonify({
            "message": "A idade mínima permitida é de 12 anos."
        }), 400

    if nova_senha and not senha_atual:
        return jsonify({
            "message": "Para alterar a senha, informe a senha atual."
        }), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, nome, email, senha, cpf, data_nascimento, telefone, fk_papel_id
            FROM usuario
            WHERE id = %s
              AND ativo = 1
            LIMIT 1
            """,
            (usuario["id"],)
        )

        usuario_banco = cursor.fetchone()

        if not usuario_banco:
            return jsonify({
                "message": "Usuário não encontrado."
            }), 404

        cursor.execute(
            """
            SELECT id
            FROM usuario
            WHERE email = %s
              AND id != %s
            LIMIT 1
            """,
            (email, usuario["id"])
        )

        email_existente = cursor.fetchone()
        cpf = somente_numeros(usuario_banco.get("cpf"))
        data_nascimento_atual = usuario_banco.get("data_nascimento")
        if data_nascimento_atual:
            data_nascimento_atual = data_nascimento_atual.strftime("%Y-%m-%d")
        else:
            data_nascimento_atual = ""

        if email_existente:
            return jsonify({
                "message": "Este e-mail já está sendo usado por outro usuário."
            }), 400

        if (
            nome == str(usuario_banco.get("nome") or "").strip()
            and email == str(usuario_banco.get("email") or "").strip().lower()
            and telefone == somente_numeros(usuario_banco.get("telefone"))
            and data_nascimento == data_nascimento_atual
            and not nova_senha
        ):
            return jsonify({
                "message": "Nenhum dado foi atualizado."
            }), 400

        if nova_senha:
            if not verificar_senha(senha_atual, usuario_banco.get("senha")):
                return jsonify({
                    "message": "Senha atual incorreta."
                }), 403

            if verificar_senha(nova_senha, usuario_banco.get("senha")):
                return jsonify({
                    "message": "A nova senha não pode ser igual à senha atual."
                }), 400

            cursor.execute(
                """
                UPDATE usuario
                SET nome = %s,
                    email = %s,
                    telefone = %s,
                    data_nascimento = %s,
                    cpf = %s,
                    senha = %s
                WHERE id = %s
                """,
                (nome, email, telefone, data_nascimento_date, cpf, gerar_hash_senha(nova_senha), usuario["id"])
            )

        else:
            cursor.execute(
                """
                UPDATE usuario
                SET nome = %s,
                    email = %s,
                    telefone = %s,
                    data_nascimento = %s,
                    cpf = %s
                WHERE id = %s
                """,
                (nome, email, telefone, data_nascimento_date, cpf, usuario["id"])
            )

        conexao.commit()

        cursor.execute(
            """
            SELECT 
                usuario.id,
                usuario.nome,
                usuario.email,
                usuario.fk_papel_id AS fk_papel_id,
                papel.descricao AS papel
            FROM usuario
            INNER JOIN papel
                ON papel.id = usuario.fk_papel_id
            WHERE usuario.id = %s
            LIMIT 1
            """,
            (usuario["id"],)
        )

        usuario_atualizado = cursor.fetchone()

        token, payload = gerar_token(usuario_atualizado)

        return jsonify({
            "message": "Perfil atualizado com sucesso.",
            "token": token,
            "usuario": {
                "id": usuario_atualizado["id"],
                "nome": usuario_atualizado["nome"],
                "email": usuario_atualizado["email"],
                "papel": usuario_atualizado["papel"],
                "papel_id": usuario_atualizado.get("fk_papel_id")
            },
            "sessao": {
                "inicio": payload["iat"],
                "expiracao": payload["exp"]
            }
        }), 200

    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()

        print("Erro no banco:", erro)

        return jsonify({
            "message": "Erro ao atualizar perfil.",
            "erro": str(erro)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexao and conexao.is_connected():
            conexao.close()


@login_bp.post("/api/logout")
@token_obrigatorio
def logout(usuario):
    return jsonify({
        "message": "Logout realizado com sucesso."
    }), 200


@login_bp.get("/api/coordenador")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def area_coordenador(usuario):
    return jsonify({
        "message": "Acesso permitido para coordenador.",
        "usuario": usuario
    }), 200
