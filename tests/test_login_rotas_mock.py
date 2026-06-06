from datetime import date

from backend.app import app
from backend import login
from backend import seguranca


class CursorFake:
    def __init__(self, fetchone_result=None):
        self.fetchone_result = fetchone_result
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchone(self):
        return self.fetchone_result

    def close(self):
        pass


class ConexaoFake:
    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self, dictionary=True):
        return self._cursor

    def commit(self):
        pass

    def rollback(self):
        pass

    def is_connected(self):
        return True

    def close(self):
        pass


def test_login_email_nao_informado():
    cliente = app.test_client()

    resposta = cliente.post("/api/login", json={"senha": "123456"})

    assert resposta.status_code == 400
    assert "e-mail" in resposta.get_json()["message"].lower()


def test_login_senha_nao_informada():
    cliente = app.test_client()

    resposta = cliente.post("/api/login", json={"email": "teste@email.com"})

    assert resposta.status_code == 400
    assert "senha" in resposta.get_json()["message"].lower()


def test_login_usuario_nao_encontrado(monkeypatch):
    cursor = CursorFake(fetchone_result=None)
    monkeypatch.setattr(login, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()

    resposta = cliente.post(
        "/api/login",
        json={
            "email": "naoexiste@email.com",
            "senha": "123456"
        }
    )

    assert resposta.status_code in [401, 404]


def test_login_senha_incorreta(monkeypatch):
    usuario = {
        "id": 1,
        "nome": "Mirella",
        "email": "mirella@email.com",
        "senha": seguranca.gerar_hash_senha("senha-correta"),
        "papel": "aluno",
        "fk_papel_id": 3,
        "ativo": 1,
        "data_nascimento": date(2005, 8, 2),
    }

    cursor = CursorFake(fetchone_result=usuario)
    monkeypatch.setattr(login, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()

    resposta = cliente.post(
        "/api/login",
        json={
            "email": "mirella@email.com",
            "senha": "senha-errada"
        }
    )

    assert resposta.status_code == 401


def test_login_com_sucesso(monkeypatch):
    usuario = {
        "id": 1,
        "nome": "Mirella",
        "email": "mirella@email.com",
        "senha": seguranca.gerar_hash_senha("123456"),
        "papel": "aluno",
        "fk_papel_id": 3,
        "ativo": 1,
        "data_nascimento": date(2005, 8, 2),
    }

    cursor = CursorFake(fetchone_result=usuario)
    monkeypatch.setattr(login, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()

    resposta = cliente.post(
        "/api/login",
        json={
            "email": "mirella@email.com",
            "senha": "123456"
        }
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert "token" in dados
    assert dados["usuario"]["nome"] == "Mirella"


def test_usuario_logado_com_token_valido(monkeypatch):
    usuario = {
        "id": 1,
        "nome": "Mirella",
        "email": "mirella@email.com",
        "papel": "aluno",
        "papel_id": 3,
    }

    monkeypatch.setattr(login, "validar_token", lambda token: usuario)

    cliente = app.test_client()

    resposta = cliente.get(
        "/api/usuario-logado",
        headers={"Authorization": "Bearer token-valido"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["usuario"]["nome"] == "Mirella"


def test_logout_com_token_valido(monkeypatch):
    monkeypatch.setattr(login, "validar_token", lambda token: {"id": 1})

    cliente = app.test_client()

    resposta = cliente.post(
        "/api/logout",
        headers={"Authorization": "Bearer token-valido"}
    )

    assert resposta.status_code in [200, 204]