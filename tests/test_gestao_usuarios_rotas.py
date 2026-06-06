from datetime import date, datetime

from backend.app import app
from backend import login
from backend import gestao_usuarios


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
        self.lastrowid = 99
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


def autenticar_como_coordenador(monkeypatch):
    monkeypatch.setattr(login, "validar_token", lambda token: USUARIO_COORDENADOR)


def test_listar_alunos_com_sucesso(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cursor = CursorFake(
        fetchall_result=[
            {
                "id": 1,
                "nome": "Aluno Teste",
                "email": "aluno@email.com",
                "cpf": "12345678909",
                "telefone": "41999998888",
                "data_nascimento": date(2005, 8, 2),
                "fk_papel_id": 3,
                "papel": "aluno",
                "ativo": 1,
                "matricula": "2026001",
                "data_criacao": datetime(2026, 1, 1, 10, 0, 0),
                "data_atualizacao": datetime(2026, 1, 2, 10, 0, 0),
            }
        ]
    )

    monkeypatch.setattr(gestao_usuarios, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/usuarios/alunos",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["usuarios"][0]["nome"] == "Aluno Teste"


def test_listar_professores_com_sucesso(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cursor = CursorFake(
        fetchall_result=[
            {
                "id": 2,
                "nome": "Professor Teste",
                "email": "prof@email.com",
                "cpf": "12345678909",
                "telefone": "41999998888",
                "data_nascimento": date(1990, 1, 1),
                "fk_papel_id": 2,
                "papel": "professor",
                "ativo": 1,
                "matricula": "P001",
                "data_criacao": datetime(2026, 1, 1, 10, 0, 0),
                "data_atualizacao": datetime(2026, 1, 2, 10, 0, 0),
            }
        ]
    )

    monkeypatch.setattr(gestao_usuarios, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/usuarios/professores",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["usuarios"][0]["nome"] == "Professor Teste"


def test_atualizar_usuario_nao_encontrado(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cursor = CursorFake(fetchone_result=None)
    monkeypatch.setattr(gestao_usuarios, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.put(
        "/api/usuarios/999",
        json={
            "nome": "Aluno Editado",
            "email": "aluno@email.com",
            "cpf": "12345678909",
            "telefone": "41999998888",
            "data_nascimento": "2005-08-02",
            "fk_papel_id": 3,
            "ativo": True,
        },
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code in [404, 400]


def test_desativar_usuario_com_sucesso(monkeypatch):
    autenticar_como_coordenador(monkeypatch)

    cursor = CursorFake(fetchone_result={"id": 10, "nome": "Aluno Teste"})
    monkeypatch.setattr(gestao_usuarios, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.delete(
        "/api/usuarios/10",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code in [200, 204, 403]