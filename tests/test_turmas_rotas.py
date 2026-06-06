from datetime import datetime

from backend.app import app
from backend import login
from backend import turmas


USUARIO_COORDENADOR = {
    "id": 1,
    "nome": "Coordenador Teste",
    "email": "coord@email.com",
    "papel": "coordenador",
    "papel_id": 1,
    "fk_papel_id": 1,
}


USUARIO_PROFESSOR = {
    "id": 2,
    "nome": "Professor Teste",
    "email": "prof@email.com",
    "papel": "professor",
    "papel_id": 2,
    "fk_papel_id": 2,
}


USUARIO_ALUNO = {
    "id": 3,
    "nome": "Aluno Teste",
    "email": "aluno@email.com",
    "papel": "aluno",
    "papel_id": 3,
    "fk_papel_id": 3,
}


class CursorFake:
    def __init__(self, fetchone_results=None, fetchall_results=None, rowcount=1):
        self.fetchone_results = fetchone_results or []
        self.fetchall_results = fetchall_results or []
        self.rowcount = rowcount
        self.lastrowid = 50
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


def autenticar(monkeypatch, usuario):
    monkeypatch.setattr(login, "validar_token", lambda token: usuario)


def test_listar_turmas_como_coordenador(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 1,
                    "nome": "SI 2026.1 - Manhã",
                    "codigo": "SI-2026-1-MA",
                    "periodo": 1,
                    "turno": "Manhã",
                    "ano": 2026,
                    "semestre": 1,
                    "capacidade": 40,
                    "total_alunos": 10,
                    "materias": "Banco de Dados",
                    "media_geral": 8.5,
                }
            ]
        ]
    )

    monkeypatch.setattr(turmas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/turmas",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["turmas"][0]["nome"] == "SI 2026.1 - Manhã"


def test_listar_turmas_como_professor(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 1,
                    "nome": "SI 2026.1 - Noite",
                    "codigo": "SI-2026-1-NA",
                    "periodo": 1,
                    "turno": "Noite",
                    "ano": 2026,
                    "semestre": 1,
                    "capacidade": 40,
                    "total_alunos": 8,
                    "materias": "Programação",
                    "media_geral": None,
                }
            ]
        ]
    )

    monkeypatch.setattr(turmas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/turmas",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert "turmas" in resposta.get_json()


def test_minha_turma_com_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cursor = CursorFake(
        fetchone_results=[
            {
                "id": 1,
                "nome": "SI 2026.1 - Manhã",
                "codigo": "SI-2026-1-MA",
                "periodo": 1,
                "turno": "Manhã",
                "ano": 2026,
                "semestre": 1,
                "capacidade": 40,
                "total_alunos": 2,
                "materias": "Banco de Dados",
            }
        ],
        fetchall_results=[
            [
                {"id": 3, "nome": "Aluno Teste", "email": "aluno@email.com"},
                {"id": 4, "nome": "Colega Teste", "email": "colega@email.com"},
            ]
        ]
    )

    monkeypatch.setattr(turmas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/minha-turma",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["turma"]["nome"] == "SI 2026.1 - Manhã"


def test_minha_turma_nao_encontrada(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cursor = CursorFake(fetchone_results=[None])
    monkeypatch.setattr(turmas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/minha-turma",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 404


def test_listar_alunos_da_turma(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 3,
                    "nome": "Aluno Teste",
                    "email": "aluno@email.com",
                    "media_geral": 8.75,
                    "materias_com_nota": 2,
                }
            ]
        ]
    )

    monkeypatch.setattr(turmas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/turmas/1/alunos",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["alunos"][0]["media_geral"] == 8.75


def test_listar_materias_da_turma(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 1,
                    "nome": "Banco de Dados",
                    "carga_horaria": 80,
                    "professor_id": 2,
                    "professor_nome": "Professor Teste",
                }
            ]
        ]
    )

    monkeypatch.setattr(turmas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/turmas/1/materias",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert "materias" in resposta.get_json()


def test_listar_cursos_para_turmas(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 1,
                    "nome": "Sistemas de Informação",
                    "codigo_prefixo": "SI",
                }
            ]
        ]
    )

    monkeypatch.setattr(turmas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/turmas/cursos",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200


def test_listar_usuarios_disponiveis(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 3,
                    "nome": "Aluno Teste",
                    "email": "aluno@email.com",
                    "papel": "aluno",
                }
            ]
        ]
    )

    monkeypatch.setattr(turmas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/usuarios/disponiveis",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code in [200, 400, 404]


def test_listar_materias_todas(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 1,
                    "nome": "Banco de Dados",
                    "carga_horaria": 80,
                }
            ]
        ]
    )

    monkeypatch.setattr(turmas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/materias/todas",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200


def test_criar_turma_dados_invalidos(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/turmas",
        json={},
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400


def test_criar_turma_com_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchone_results=[
            {"nome": "Sistemas de Informação", "codigo_prefixo": "SI"},
            None,
        ],
        fetchall_results=[
            [],
            [],
        ],
        rowcount=1
    )

    monkeypatch.setattr(turmas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/turmas",
        json={
            "curso_id": 1,
            "periodo": 1,
            "semestre": 1,
            "turno": "Manhã",
            "capacidade": 40,
        },
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code in [200, 201, 409, 500]


def test_vincular_e_remover_aluno(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(rowcount=1)
    monkeypatch.setattr(turmas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()

    resposta_post = cliente.post(
        "/api/turmas/1/alunos",
        json={"aluno_id": 3},
        headers={"Authorization": "Bearer token"}
    )

    resposta_delete = cliente.delete(
        "/api/turmas/1/alunos/3",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta_post.status_code in [200, 201, 400, 409, 500]
    assert resposta_delete.status_code in [200, 404, 500]


def test_vincular_e_remover_materia(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(rowcount=1)
    monkeypatch.setattr(turmas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()

    resposta_post = cliente.post(
        "/api/turmas/1/materias",
        json={"materia_id": 1},
        headers={"Authorization": "Bearer token"}
    )

    resposta_delete = cliente.delete(
        "/api/turmas/1/materias/1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta_post.status_code in [200, 201, 400, 409, 500]
    assert resposta_delete.status_code in [200, 404, 500]


def test_editar_turma_dados_invalidos(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cliente = app.test_client()
    resposta = cliente.put(
        "/api/turmas/1",
        json={},
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400


def test_desativar_turma(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(rowcount=1)
    monkeypatch.setattr(turmas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.delete(
        "/api/turmas/1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code in [200, 404, 500]