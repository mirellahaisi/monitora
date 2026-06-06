from datetime import datetime

from backend.app import app
from backend import login
from backend import cursos
from backend import materias


USUARIO_COORDENADOR = {
    "id": 1,
    "nome": "Coordenador Teste",
    "email": "coord@email.com",
    "papel": "coordenador",
    "papel_id": 1,
}


class CursorFake:
    def __init__(self, fetchone_result=None, fetchall_result=None):
        self.fetchone_result = fetchone_result
        self.fetchall_result = fetchall_result or []
        self.lastrowid = 10
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchone(self):
        if isinstance(self.fetchone_result, list):
            if self.fetchone_result:
                return self.fetchone_result.pop(0)
            return None
        return self.fetchone_result

    def fetchall(self):
        return self.fetchall_result

    def close(self):
        pass


class ConexaoFake:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self, dictionary=True):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def is_connected(self):
        return True

    def close(self):
        self.closed = True


def autenticar_como_coordenador(monkeypatch):
    monkeypatch.setattr(login, "validar_token", lambda token: USUARIO_COORDENADOR)


def test_listar_cursos_com_sucesso(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cursor = CursorFake(
        fetchall_result=[
            {
                "id": 1,
                "nome": "Sistemas de Informação",
                "codigo_prefixo": "SI",
                "ativo": 1,
                "data_criacao": datetime(2026, 1, 1, 10, 0, 0),
                "data_atualizacao": datetime(2026, 1, 2, 10, 0, 0),
            }
        ]
    )

    monkeypatch.setattr(cursos, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/cursos",
        headers={"Authorization": "Bearer token-teste"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["cursos"][0]["nome"] == "Sistemas de Informação"
    assert dados["cursos"][0]["ativo"] is True


def test_criar_curso_com_dados_invalidos(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/cursos",
        json={"nome": "SI", "codigo_prefixo": ""},
        headers={"Authorization": "Bearer token-teste"}
    )

    assert resposta.status_code == 400
    assert "message" in resposta.get_json()


def test_criar_curso_com_sucesso(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cursor = CursorFake(fetchone_result=[None, None])
    monkeypatch.setattr(cursos, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/cursos",
        json={
            "nome": "Sistemas de Informação",
            "codigo_prefixo": "SI",
            "ativo": True
        },
        headers={"Authorization": "Bearer token-teste"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 201
    assert dados["id"] == 10
    assert "sucesso" in dados["message"]


def test_atualizar_curso_nao_encontrado(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cursor = CursorFake(fetchone_result=[None])
    monkeypatch.setattr(cursos, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.put(
        "/api/cursos/99",
        json={
            "nome": "Sistemas de Informação",
            "codigo_prefixo": "SI",
            "ativo": True
        },
        headers={"Authorization": "Bearer token-teste"}
    )

    assert resposta.status_code == 404


def test_excluir_curso_com_sucesso(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cursor = CursorFake(
        fetchone_result=[
            {"id": 1, "nome": "Sistemas de Informação"},
            {"total": 0},
        ]
    )
    monkeypatch.setattr(cursos, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.delete(
        "/api/cursos/1",
        headers={"Authorization": "Bearer token-teste"}
    )

    assert resposta.status_code == 200
    assert "sucesso" in resposta.get_json()["message"]


def test_listar_materias_com_sucesso(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cursor = CursorFake(
        fetchall_result=[
            {
                "id": 1,
                "nome": "Banco de Dados",
                "codigo": "BD",
                "carga_horaria": 80,
                "descricao": "Disciplina de banco de dados",
                "ativo": 1,
                "data_criacao": datetime(2026, 1, 1, 10, 0, 0),
                "data_atualizacao": datetime(2026, 1, 2, 10, 0, 0),
            }
        ]
    )

    monkeypatch.setattr(materias, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/materias",
        headers={"Authorization": "Bearer token-teste"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["materias"][0]["nome"] == "Banco de Dados"
    assert dados["materias"][0]["ativo"] is True
    assert dados["materias"][0]["carga_horaria"] == 80


def test_criar_materia_com_dados_invalidos(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/materias",
        json={"nome": "BD", "codigo": "", "carga_horaria": 0},
        headers={"Authorization": "Bearer token-teste"}
    )

    assert resposta.status_code == 400
    assert "message" in resposta.get_json()


def test_criar_materia_com_sucesso(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cursor = CursorFake(fetchone_result=[None, None])
    monkeypatch.setattr(materias, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/materias",
        json={
            "nome": "Banco de Dados",
            "codigo": "BD",
            "carga_horaria": 80,
            "descricao": "Disciplina de banco de dados",
            "ativo": True
        },
        headers={"Authorization": "Bearer token-teste"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 201
    assert dados["id"] == 10
    assert "sucesso" in dados["message"]


def test_atualizar_materia_nao_encontrada(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cursor = CursorFake(fetchone_result=[None])
    monkeypatch.setattr(materias, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.put(
        "/api/materias/99",
        json={
            "nome": "Banco de Dados",
            "codigo": "BD",
            "carga_horaria": 80,
            "descricao": "Disciplina",
            "ativo": True
        },
        headers={"Authorization": "Bearer token-teste"}
    )

    assert resposta.status_code == 404


def test_excluir_materia_com_sucesso(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cursor = CursorFake(
        fetchone_result=[
            {"id": 1, "nome": "Banco de Dados"},
            {"total": 0},
            {"total": 0},
        ]
    )
    monkeypatch.setattr(materias, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.delete(
        "/api/materias/1",
        headers={"Authorization": "Bearer token-teste"}
    )

    assert resposta.status_code == 200
    assert "sucesso" in resposta.get_json()["message"]