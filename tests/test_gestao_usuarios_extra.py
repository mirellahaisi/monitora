from datetime import date, datetime
from decimal import Decimal

from backend.app import app
from backend import login
import backend.gestao_usuarios as gu


USUARIO_ADMIN = {
    "id": 1,
    "nome": "Admin Teste",
    "email": "admin@email.com",
    "papel": "admin",
    "papel_id": 1,
}

USUARIO_COORDENADOR = {
    "id": 2,
    "nome": "Coordenador Teste",
    "email": "coord@email.com",
    "papel": "coordenador",
    "papel_id": 1,
}


class CursorFake:
    def __init__(self, fetchone_results=None, fetchall_results=None, rowcount=1):
        self.fetchone_results = fetchone_results or []
        self.fetchall_results = fetchall_results or []
        self.rowcount = rowcount
        self.lastrowid = 99
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchone(self):
        if self.fetchone_results:
            return self.fetchone_results.pop(0)
        return None

    def fetchall(self):
        if self.fetchall_results:
            return self.fetchall_results.pop(0)
        return []

    def close(self):
        pass


class ConexaoFake:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False

    def cursor(self, dictionary=True):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def is_connected(self):
        return True

    def close(self):
        pass


def autenticar_admin(monkeypatch):
    monkeypatch.setattr(login, "validar_token", lambda token: USUARIO_ADMIN)


def autenticar_coordenador(monkeypatch):
    monkeypatch.setattr(login, "validar_token", lambda token: USUARIO_COORDENADOR)


def dados_aluno_validos():
    return {
        "nome": "Aluno Teste",
        "cpf": "52998224725",
        "email": "aluno@email.com",
        "telefone": "41999998888",
        "data_nascimento": "2005-08-02",
    }


def dados_professor_validos():
    return {
        "nome": "Professor Teste",
        "cpf": "52998224725",
        "email": "prof@email.com",
        "telefone": "41999998888",
        "data_nascimento": "1990-01-01",
        "especialidade": "Matemática",
        "salario": "3500,50",
    }


# ==========================
# HELPERS
# ==========================

def test_parse_salario():
    assert gu._parse_salario("R$ 3.500,50") == Decimal("3500.50")
    assert gu._parse_salario("3500.50") == Decimal("3500.50")
    assert gu._parse_salario("") is None
    assert gu._parse_salario("-10") is None
    assert gu._parse_salario("abc") is None


def test_normalizar_dados_aluno():
    dados = gu._normalizar_dados_usuario(dados_aluno_validos(), "aluno")

    assert dados["nome"] == "Aluno Teste"
    assert dados["cpf"] == "52998224725"
    assert dados["email"] == "aluno@email.com"
    assert dados["especialidade"] is None
    assert dados["salario"] is None


def test_normalizar_dados_professor():
    dados = gu._normalizar_dados_usuario(dados_professor_validos(), "professor")

    assert dados["nome"] == "Professor Teste"
    assert dados["especialidade"] == "Matemática"
    assert dados["salario"] == Decimal("3500.50")


def test_validar_dados_usuario_invalidos():
    dados = {
        "nome": "A",
        "cpf": "111",
        "email": "email-invalido",
        "telefone": "123",
        "data_nascimento": "2026-01-01",
        "especialidade": "",
        "salario": None,
    }

    erros = gu._validar_dados_usuario(dados, "professor")

    assert len(erros) >= 5


def test_validar_dados_usuario_aluno_valido():
    dados = gu._normalizar_dados_usuario(dados_aluno_validos(), "aluno")
    erros = gu._validar_dados_usuario(dados, "aluno")

    assert erros == []


def test_validar_dados_usuario_professor_valido():
    dados = gu._normalizar_dados_usuario(dados_professor_validos(), "professor")
    erros = gu._validar_dados_usuario(dados, "professor")

    assert erros == []


def test_estado_usuario_para_comparacao():
    estado = gu._estado_usuario_para_comparacao({
        "nome": "  Aluno Teste ",
        "cpf": "529.982.247-25",
        "email": "ALUNO@EMAIL.COM",
        "telefone": "(41) 99999-8888",
        "data_nascimento": date(2005, 8, 2),
        "papel": "aluno",
        "especialidade": "Ignorar",
        "salario": "1000",
    })

    assert estado["nome"] == "Aluno Teste"
    assert estado["cpf"] == "52998224725"
    assert estado["email"] == "aluno@email.com"
    assert estado["especialidade"] is None
    assert estado["salario"] is None


def test_estado_payload_para_comparacao():
    dados = gu._normalizar_dados_usuario(dados_professor_validos(), "professor")
    estado = gu._estado_payload_para_comparacao(dados)

    assert estado["nome"] == "Professor Teste"
    assert estado["salario"] == "3500.50"


def test_mensagem_erro_mysql():
    assert "CPF" in gu._mensagem_erro_mysql("Duplicate entry for key 'cpf'", "Erro")
    assert "e-mail" in gu._mensagem_erro_mysql("Duplicate entry for key 'email'", "Erro")
    assert gu._mensagem_erro_mysql("outro erro", "Erro padrão") == "Erro padrão"


def test_validar_unicidade_sem_duplicidade():
    cursor = CursorFake(fetchone_results=[None, None])
    conexao = ConexaoFake(cursor)

    erro = gu._validar_unicidade_usuario(conexao, "52998224725", "teste@email.com")

    assert erro is None


def test_validar_unicidade_cpf_duplicado():
    cursor = CursorFake(fetchone_results=[{"id": 1}])
    conexao = ConexaoFake(cursor)

    erro = gu._validar_unicidade_usuario(conexao, "52998224725", "teste@email.com")

    assert "CPF" in erro


def test_validar_unicidade_email_duplicado():
    cursor = CursorFake(fetchone_results=[None, {"id": 1}])
    conexao = ConexaoFake(cursor)

    erro = gu._validar_unicidade_usuario(conexao, "52998224725", "teste@email.com")

    assert "e-mail" in erro


def test_buscar_usuario_existente():
    usuario = {
        "id": 1,
        "nome": "Aluno Teste",
        "cpf": "52998224725",
        "email": "aluno@email.com",
        "telefone": "41999998888",
        "data_nascimento": date(2005, 8, 2),
        "papel": "aluno",
        "especialidade": None,
        "salario": None,
    }

    cursor = CursorFake(fetchone_results=[usuario])
    conexao = ConexaoFake(cursor)

    resultado = gu._buscar_usuario_existente(conexao, 1)

    assert resultado["nome"] == "Aluno Teste"


# ==========================
# CRIAR USUÁRIO
# ==========================

def test_criar_usuario_com_papel_dados_invalidos():
    resultado = gu._criar_usuario_com_papel(
        {
            "nome": "A",
            "cpf": "111",
            "email": "errado",
            "telefone": "1",
            "data_nascimento": "2026-01-01",
        },
        3
    )

    assert resultado["status"] == 400


def test_criar_usuario_com_papel_sucesso(monkeypatch):
    cursor = CursorFake(fetchone_results=[None, None])
    monkeypatch.setattr(gu, "criar_conexao", lambda: ConexaoFake(cursor))

    resultado = gu._criar_usuario_com_papel(dados_aluno_validos(), 3)

    assert resultado["status"] == 201
    assert resultado["senha_inicial"] == "020805"


def test_rota_criar_aluno_sucesso(monkeypatch):
    autenticar_admin(monkeypatch)

    cursor = CursorFake(fetchone_results=[None, None])
    monkeypatch.setattr(gu, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/usuarios/alunos",
        json=dados_aluno_validos(),
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 201
    assert "senha_inicial" in resposta.get_json()


def test_rota_criar_professor_sucesso(monkeypatch):
    autenticar_admin(monkeypatch)

    cursor = CursorFake(fetchone_results=[None, None])
    monkeypatch.setattr(gu, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/usuarios/professores",
        json=dados_professor_validos(),
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 201
    assert "senha_inicial" in resposta.get_json()


def test_rota_criar_coordenador_sucesso(monkeypatch):
    autenticar_admin(monkeypatch)

    dados = dados_professor_validos()
    dados["email"] = "coord@email.com"

    cursor = CursorFake(fetchone_results=[None, None])
    monkeypatch.setattr(gu, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/usuarios/coordenacao",
        json=dados,
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 201


# ==========================
# BUSCAR / ATUALIZAR / DELETAR
# ==========================

def test_buscar_usuario_rota_nao_encontrado(monkeypatch):
    autenticar_admin(monkeypatch)

    cursor = CursorFake(fetchone_results=[None])
    monkeypatch.setattr(gu, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/usuarios/999",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 404


def test_buscar_usuario_rota_sucesso(monkeypatch):
    autenticar_admin(monkeypatch)

    cursor = CursorFake(
        fetchone_results=[
            {
                "id": 1,
                "nome": "Professor Teste",
                "cpf": "52998224725",
                "email": "prof@email.com",
                "telefone": "41999998888",
                "data_nascimento": date(1990, 1, 1),
                "especialidade": "Matemática",
                "salario": Decimal("3500.50"),
                "papel": "professor",
            }
        ]
    )

    monkeypatch.setattr(gu, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/usuarios/1",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["usuario"]["cpf"] == "529.982.247-25"
    assert dados["usuario"]["telefone"] == "(41) 99999-8888"


def test_atualizar_usuario_nao_encontrado(monkeypatch):
    autenticar_admin(monkeypatch)

    cursor = CursorFake(fetchone_results=[None])
    monkeypatch.setattr(gu, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.put(
        "/api/usuarios/999",
        json=dados_aluno_validos(),
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 404


def test_atualizar_usuario_sem_alteracao(monkeypatch):
    autenticar_admin(monkeypatch)

    usuario_atual = {
        "id": 1,
        "nome": "Aluno Teste",
        "cpf": "52998224725",
        "email": "aluno@email.com",
        "telefone": "41999998888",
        "data_nascimento": date(2005, 8, 2),
        "papel": "aluno",
        "especialidade": None,
        "salario": None,
    }

    cursor = CursorFake(fetchone_results=[usuario_atual, None, None])
    monkeypatch.setattr(gu, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.put(
        "/api/usuarios/1",
        json=dados_aluno_validos(),
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["alterado"] is False


def test_atualizar_usuario_sucesso(monkeypatch):
    autenticar_admin(monkeypatch)

    usuario_atual = {
        "id": 1,
        "nome": "Aluno Antigo",
        "cpf": "52998224725",
        "email": "aluno@email.com",
        "telefone": "41999998888",
        "data_nascimento": date(2005, 8, 2),
        "papel": "aluno",
        "especialidade": None,
        "salario": None,
    }

    novos_dados = dados_aluno_validos()
    novos_dados["nome"] = "Aluno Novo"

    cursor = CursorFake(fetchone_results=[usuario_atual, None, None])
    monkeypatch.setattr(gu, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.put(
        "/api/usuarios/1",
        json=novos_dados,
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["alterado"] is True


def test_deletar_usuario_sem_permissao_coordenador(monkeypatch):
    autenticar_coordenador(monkeypatch)

    cliente = app.test_client()
    resposta = cliente.delete(
        "/api/usuarios/1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 403


def test_deletar_usuario_nao_encontrado(monkeypatch):
    autenticar_admin(monkeypatch)

    cursor = CursorFake(rowcount=0)
    monkeypatch.setattr(gu, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.delete(
        "/api/usuarios/999",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 404


def test_deletar_usuario_sucesso(monkeypatch):
    autenticar_admin(monkeypatch)

    cursor = CursorFake(rowcount=1)
    monkeypatch.setattr(gu, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.delete(
        "/api/usuarios/1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200