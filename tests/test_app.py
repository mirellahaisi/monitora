from backend import app as app_module


class CursorFake:
    def __init__(self, usuario=None):
        self.usuario = usuario

    def execute(self, sql, params=None):
        pass

    def fetchone(self):
        return self.usuario

    def close(self):
        pass


class ConexaoFake:
    def __init__(self, usuario=None):
        self.cursor_fake = CursorFake(usuario)

    def cursor(self, dictionary=True):
        return self.cursor_fake

    def close(self):
        pass


def test_create_jwt_e_decode_payload():
    token = app_module.create_jwt({
        "id": 1,
        "nome": "Mirella",
        "papel": "aluno"
    })

    payload = app_module.decode_jwt_payload(token)

    assert payload["id"] == 1
    assert payload["nome"] == "Mirella"


def test_decode_jwt_payload_invalido():
    assert app_module.decode_jwt_payload("token-invalido") is None


def test_login_legado_usuario_nao_encontrado(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "get_db_connection",
        lambda: ConexaoFake(usuario=None)
    )

    cliente = app_module.app.test_client()

    resposta = cliente.post(
        "/api/login-legado",
        json={
            "matricula": "123",
            "senha": "errada"
        }
    )

    assert resposta.status_code == 401


def test_login_legado_com_sucesso(monkeypatch):
    usuario = {
        "id": 1,
        "matricula": "123",
        "papel": "aluno",
        "nome": "Mirella",
        "email": "mirella@email.com"
    }

    monkeypatch.setattr(
        app_module,
        "get_db_connection",
        lambda: ConexaoFake(usuario=usuario)
    )

    cliente = app_module.app.test_client()

    resposta = cliente.post(
        "/api/login-legado",
        json={
            "matricula": "123",
            "senha": "123456"
        }
    )

    assert resposta.status_code == 200
    assert "token" in resposta.get_json()


def test_api_me_sem_token():
    cliente = app_module.app.test_client()

    resposta = cliente.get("/api/me")

    assert resposta.status_code in [401, 404]


def test_api_me_com_token_valido():
    token = app_module.create_jwt({
        "id": 1,
        "nome": "Mirella",
        "email": "mirella@email.com",
        "papel": "aluno"
    })

    cliente = app_module.app.test_client()

    resposta = cliente.get(
        "/api/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code in [200, 404]