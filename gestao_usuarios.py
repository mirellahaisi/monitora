from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re

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
                papel.descricao AS papel,
                MAX(turma.nome) AS turma
            FROM usuario
            INNER JOIN papel
                ON papel.id = usuario.fk_papel_id
            LEFT JOIN usuario_turma
                ON usuario_turma.fk_usuario_id = usuario.id
            LEFT JOIN turma
                ON turma.id = usuario_turma.fk_turma_id
               AND turma.ativo = 1
            WHERE LOWER(papel.descricao) IN ({placeholders})
              AND usuario.ativo = 1
            GROUP BY
                usuario.id,
                usuario.nome,
                usuario.cpf,
                usuario.email,
                usuario.telefone,
                usuario.data_nascimento,
                usuario.especialidade,
                usuario.salario,
                usuario.data_criacao,
                papel.descricao
            ORDER BY usuario.nome ASC
            """,
            [p.lower() for p in papeis]
        )

        usuarios = cursor.fetchall()

        for u in usuarios:
            u["cpf"] = _formatar_cpf(u.get("cpf"))
            u["telefone"] = _formatar_telefone(u.get("telefone"))
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
    return render_template("pages/gestao_usuarios.html", active_page='gestao_usuarios')


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



# Helpers de validacao -------------------------------------------------------

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
SALARIO_QUANTIZE = Decimal("0.01")


def somente_numeros(valor):
    return "".join(filter(str.isdigit, str(valor or "")))


def _texto_limpo(valor):
    return str(valor or "").strip()


def _formatar_cpf(valor):
    numeros = somente_numeros(valor)
    if len(numeros) != 11:
        return _texto_limpo(valor) or None
    return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"


def _formatar_telefone(valor):
    numeros = somente_numeros(valor)
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    if len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    return _texto_limpo(valor) or None


def _papel_por_fk(fk_papel_id):
    if fk_papel_id == 3:
        return "aluno"
    if fk_papel_id == 2:
        return "professor"
    return "coordenador"


def _papel_eh_coordenacao(papel):
    return str(papel or "").lower() in ("admin", "adm", "coordenador")


def _papel_exige_campos_profissionais(papel):
    return str(papel or "").lower() != "aluno"


def _email_valido(email):
    return bool(EMAIL_RE.match(_texto_limpo(email)))


def _telefone_valido(telefone):
    return len(somente_numeros(telefone)) in (10, 11)


def _cpf_valido(cpf):
    numeros = somente_numeros(cpf)
    if len(numeros) != 11 or len(set(numeros)) == 1:
        return False

    soma = sum(int(numeros[i]) * (10 - i) for i in range(9))
    digito_1 = (soma * 10) % 11
    digito_1 = 0 if digito_1 == 10 else digito_1

    soma = sum(int(numeros[i]) * (11 - i) for i in range(10))
    digito_2 = (soma * 10) % 11
    digito_2 = 0 if digito_2 == 10 else digito_2

    return numeros[-2:] == f"{digito_1}{digito_2}"


def _parse_data_nascimento(valor):
    if valor in (None, ""):
        return None

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    try:
        return date.fromisoformat(str(valor).strip())
    except ValueError:
        return None


def _calcular_idade(data_nascimento):
    nascimento = _parse_data_nascimento(data_nascimento)
    if not nascimento:
        return None

    hoje = date.today()
    idade = hoje.year - nascimento.year
    if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
        idade -= 1
    return idade


def _idade_minima_atingida(data_nascimento, papel):
    idade = _calcular_idade(data_nascimento)
    if idade is None:
        return False

    if str(papel or "").lower() == "aluno":
        return idade > 12

    return idade > 18


def _parse_salario(valor):
    texto = _texto_limpo(valor)
    if not texto:
        return None

    texto = texto.replace("R$", "").replace(" ", "")
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    else:
        texto = texto.replace(",", ".")

    try:
        salario = Decimal(texto).quantize(SALARIO_QUANTIZE)
    except (InvalidOperation, ValueError):
        return None

    if salario < 0:
        return None

    return salario


def _formatar_salario_para_comparacao(valor):
    salario = _parse_salario(valor)
    return f"{salario:.2f}" if salario is not None else None


def _normalizar_dados_usuario(dados, papel):
    papel_normalizado = str(papel or "").lower()
    nome = _texto_limpo(dados.get("nome"))
    cpf = somente_numeros(dados.get("cpf"))
    email = _texto_limpo(dados.get("email")).lower()
    telefone = somente_numeros(dados.get("telefone"))
    data_nascimento = _texto_limpo(dados.get("data_nascimento"))
    especialidade = _texto_limpo(dados.get("especialidade"))
    salario = _parse_salario(dados.get("salario"))

    if not _papel_exige_campos_profissionais(papel_normalizado):
        especialidade = None
        salario = None

    return {
        "nome": nome,
        "cpf": cpf,
        "email": email,
        "telefone": telefone,
        "data_nascimento": data_nascimento or None,
        "especialidade": especialidade if especialidade else None,
        "salario": salario,
        "papel": papel_normalizado,
    }


def _validar_dados_usuario(dados, papel):
    papel_normalizado = str(papel or "").lower()
    erros = []

    if len(dados["nome"]) < 3:
        erros.append("O nome deve ter no minimo 3 caracteres.")

    if not dados["cpf"]:
        erros.append("Informe o CPF.")
    elif not _cpf_valido(dados["cpf"]):
        erros.append("Informe um CPF valido.")

    if not dados["email"]:
        erros.append("Informe o e-mail.")
    elif not _email_valido(dados["email"]):
        erros.append("Informe um e-mail valido.")

    if not dados["telefone"]:
        erros.append("Informe o telefone.")
    elif not _telefone_valido(dados["telefone"]):
        erros.append("Informe um telefone valido com DDD.")

    if not dados["data_nascimento"]:
        erros.append("Informe a data de nascimento.")
    elif not _parse_data_nascimento(dados["data_nascimento"]):
        erros.append("Informe uma data de nascimento valida.")
    elif not _idade_minima_atingida(dados["data_nascimento"], papel_normalizado):
        if papel_normalizado == "aluno":
            erros.append("Alunos devem ter mais de 12 anos.")
        else:
            erros.append("Professores e coordenadores devem ter mais de 18 anos.")

    if _papel_exige_campos_profissionais(papel_normalizado):
        if len(_texto_limpo(dados.get("especialidade"))) < 3:
            erros.append("A especialidade deve ter no minimo 3 caracteres.")

        if dados["salario"] is None:
            erros.append("Informe um salario valido no formato 0,00.")

    return erros


def _buscar_usuario_existente(conexao, usuario_id):
    cursor = None
    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                u.id,
                u.nome,
                u.cpf,
                u.email,
                u.telefone,
                u.data_nascimento,
                u.especialidade,
                u.salario,
                p.descricao AS papel
            FROM usuario u
            INNER JOIN papel p ON p.id = u.fk_papel_id
            WHERE u.id = %s AND u.ativo = 1
            LIMIT 1
        """, (usuario_id,))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()


def _estado_usuario_para_comparacao(usuario):
    papel = str(usuario.get("papel") or "").lower()
    return {
        "nome": _texto_limpo(usuario.get("nome")),
        "cpf": somente_numeros(usuario.get("cpf")),
        "email": _texto_limpo(usuario.get("email")).lower(),
        "telefone": somente_numeros(usuario.get("telefone")),
        "data_nascimento": (
            _parse_data_nascimento(usuario.get("data_nascimento")).isoformat()
            if _parse_data_nascimento(usuario.get("data_nascimento"))
            else None
        ),
        "especialidade": None if not _papel_exige_campos_profissionais(papel) else (_texto_limpo(usuario.get("especialidade")) or None),
        "salario": None if not _papel_exige_campos_profissionais(papel) else _formatar_salario_para_comparacao(usuario.get("salario")),
    }


def _estado_payload_para_comparacao(dados_normalizados):
    return {
        "nome": dados_normalizados["nome"],
        "cpf": dados_normalizados["cpf"],
        "email": dados_normalizados["email"],
        "telefone": dados_normalizados["telefone"],
        "data_nascimento": dados_normalizados["data_nascimento"],
        "especialidade": dados_normalizados["especialidade"],
        "salario": _formatar_salario_para_comparacao(dados_normalizados["salario"]),
    }


def _validar_unicidade_usuario(conexao, cpf, email, usuario_id=None):
    cursor = None
    try:
        cursor = conexao.cursor(dictionary=True)

        if cpf:
            if usuario_id is None:
                cursor.execute("SELECT id FROM usuario WHERE cpf = %s LIMIT 1", (cpf,))
            else:
                cursor.execute("SELECT id FROM usuario WHERE cpf = %s AND id != %s LIMIT 1", (cpf, usuario_id))
            if cursor.fetchone():
                return "Ja existe um usuario cadastrado com este CPF."

        if email:
            if usuario_id is None:
                cursor.execute("SELECT id FROM usuario WHERE email = %s LIMIT 1", (email,))
            else:
                cursor.execute("SELECT id FROM usuario WHERE email = %s AND id != %s LIMIT 1", (email, usuario_id))
            if cursor.fetchone():
                return "Ja existe um usuario cadastrado com este e-mail."

        return None
    finally:
        if cursor:
            cursor.close()


def _mensagem_erro_mysql(erro, padrao):
    mensagem = str(erro)
    if "usuario.cpf" in mensagem or "for key 'cpf'" in mensagem.lower():
        return "Ja existe um usuario cadastrado com este CPF."
    if "usuario.email" in mensagem or "for key 'email'" in mensagem.lower():
        return "Ja existe um usuario cadastrado com este e-mail."
    return padrao


def _criar_usuario_com_papel(dados, fk_papel_id):
    papel = _papel_por_fk(fk_papel_id)
    dados_normalizados = _normalizar_dados_usuario(dados, papel)
    erros = _validar_dados_usuario(dados_normalizados, papel)
    if erros:
        return {"message": " ".join(erros), "status": 400}

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        erro_unicidade = _validar_unicidade_usuario(
            conexao,
            dados_normalizados["cpf"],
            dados_normalizados["email"],
        )
        if erro_unicidade:
            return {"message": erro_unicidade, "status": 409}

        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO usuario (
                nome, cpf, email, telefone,
                data_nascimento, especialidade,
                salario, fk_papel_id, ativo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
        """, (
            dados_normalizados["nome"],
            dados_normalizados["cpf"],
            dados_normalizados["email"],
            dados_normalizados["telefone"],
            dados_normalizados["data_nascimento"],
            dados_normalizados["especialidade"],
            dados_normalizados["salario"],
            fk_papel_id
        ))

        conexao.commit()
        return {"message": None, "status": 201}

    except mysql.connector.Error as erro:
        return {
            "message": _mensagem_erro_mysql(erro, "Erro ao salvar usuario."),
            "status": 409 if "Duplicate entry" in str(erro) else 500
        }

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


def _atualizar_usuario_validado(usuario_logado, usuario_id, dados):
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        usuario_atual = _buscar_usuario_existente(conexao, usuario_id)

        if not usuario_atual:
            return jsonify({"message": "Usuario nao encontrado."}), 404

        papel_logado = str(usuario_logado.get("papel") or "").lower()
        if papel_logado == "coordenador" and _papel_eh_coordenacao(usuario_atual.get("papel")):
            return jsonify({"message": "Coordenadores nao podem editar outros usuarios da coordenacao."}), 403

        papel_usuario = str(usuario_atual.get("papel") or "").lower()
        papel_referencia = "coordenador" if _papel_eh_coordenacao(papel_usuario) else papel_usuario

        dados_normalizados = _normalizar_dados_usuario(dados, papel_referencia)
        erros = _validar_dados_usuario(dados_normalizados, papel_referencia)
        if erros:
            return jsonify({"message": " ".join(erros)}), 400

        erro_unicidade = _validar_unicidade_usuario(
            conexao,
            dados_normalizados["cpf"],
            dados_normalizados["email"],
            usuario_id,
        )
        if erro_unicidade:
            return jsonify({"message": erro_unicidade}), 409

        estado_atual = _estado_usuario_para_comparacao(usuario_atual)
        estado_novo = _estado_payload_para_comparacao(dados_normalizados)
        if estado_atual == estado_novo:
            return jsonify({
                "message": "Nenhuma informacao foi alterada.",
                "alterado": False
            }), 200

        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE usuario
            SET nome = %s,
                cpf = %s,
                email = %s,
                telefone = %s,
                data_nascimento = %s,
                especialidade = %s,
                salario = %s
            WHERE id = %s AND ativo = 1
        """, (
            dados_normalizados["nome"],
            dados_normalizados["cpf"],
            dados_normalizados["email"],
            dados_normalizados["telefone"],
            dados_normalizados["data_nascimento"],
            dados_normalizados["especialidade"],
            dados_normalizados["salario"],
            usuario_id,
        ))
        conexao.commit()

        return jsonify({"message": "Usuario atualizado com sucesso.", "alterado": True}), 200

    except mysql.connector.Error as erro:
        return jsonify({
            "message": _mensagem_erro_mysql(erro, "Erro ao atualizar usuario."),
            "erro": str(erro)
        }), 409 if "Duplicate entry" in str(erro) else 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()

@gestao_usuarios_bp.post("/api/usuarios/alunos")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def criar_aluno(usuario_logado):
    dados = request.get_json(silent=True) or {}
    resultado = _criar_usuario_com_papel(dados, 3)

    if resultado["message"]:
        return jsonify({"message": resultado["message"]}), resultado["status"]

    return jsonify({"message": "Aluno criado com sucesso."}), 201

@gestao_usuarios_bp.post("/api/usuarios/professores")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def criar_professor(usuario_logado):
    dados = request.get_json(silent=True) or {}
    resultado = _criar_usuario_com_papel(dados, 2)

    if resultado["message"]:
        return jsonify({"message": resultado["message"]}), resultado["status"]

    return jsonify({"message": "Professor criado com sucesso."}), 201

@gestao_usuarios_bp.post("/api/usuarios/coordenacao")
@token_obrigatorio
@papel_obrigatorio("admin", "adm")
def criar_coordenador(usuario_logado):
    dados = request.get_json(silent=True) or {}
    resultado = _criar_usuario_com_papel(dados, 1)

    if resultado["message"]:
        return jsonify({"message": resultado["message"]}), resultado["status"]

    return jsonify({"message": "Coordenador criado com sucesso."}), 201

@gestao_usuarios_bp.put("/api/usuarios/<int:id>")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def atualizar_usuario(usuario_logado, id):
    dados = request.get_json(silent=True) or {}
    return _atualizar_usuario_validado(usuario_logado, id, dados)

    for campo in ("cpf", "telefone"):
        if campo in dados:
            dados[campo] = somente_numeros(dados.get(campo))


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

        usuario["cpf"] = _formatar_cpf(usuario.get("cpf"))
        usuario["telefone"] = _formatar_telefone(usuario.get("telefone"))
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
