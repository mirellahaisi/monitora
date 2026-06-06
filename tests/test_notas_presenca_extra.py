from backend.app import app
from backend import login
import backend.notas as notas
import backend.presenca as presenca


USUARIO_COORDENADOR = {
    "id": 1,
    "nome": "Coordenador Teste",
    "email": "coord@email.com",
    "papel": "coordenador",
    "papel_id": 1,
}

USUARIO_PROFESSOR = {
    "id": 2,
    "nome": "Professor Teste",
    "email": "prof@email.com",
    "papel": "professor",
    "papel_id": 2,
}


class CursorFake:
    def __init__(self, fetchall_results=None, fetchone_results=None, rowcount=1):
        self.fetchall_results = fetchall_results or []
        self.fetchone_results = fetchone_results or []
        self.rowcount = rowcount
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchall(self):
        if self.fetchall_results:
            return self.fetchall_results.pop(0)
        return []

    def fetchone(self):
        if self.fetchone_results:
            return self.fetchone_results.pop(0)
        return None

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


def test_coordenador_lista_materias(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Matemática"}
            ]
        ]
    )
    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/coordenador/materias",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["materias"][0]["nome"] == "Matemática"


def test_coordenador_turmas_sem_materia(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/coordenador/turmas",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400


def test_coordenador_turmas_com_materia(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Turma A", "periodo": 1}
            ]
        ]
    )
    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/coordenador/turmas?materia_id=1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["turmas"][0]["nome"] == "Turma A"


def test_coordenador_professores_sem_parametros(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/coordenador/professores",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400


def test_coordenador_professores_com_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 2, "nome": "Professor Teste"}
            ]
        ]
    )
    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/coordenador/professores?materia_id=1&turma_id=1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["professores"][0]["nome"] == "Professor Teste"


def test_coordenador_alunos_sem_parametros(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/coordenador/alunos",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400


def test_coordenador_alunos_com_media(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "aluno_id": 1,
                    "aluno_nome": "Aluno B",
                    "professores": "Professor",
                    "nota1": 8,
                    "nota2": 10,
                },
                {
                    "aluno_id": 2,
                    "aluno_nome": "Aluno A",
                    "professores": "Professor",
                    "nota1": None,
                    "nota2": 6,
                },
            ]
        ]
    )
    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/coordenador/alunos?materia_id=1&turma_id=1&professor_id=2",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["alunos"][0]["nome"] == "Aluno A"
    assert dados["alunos"][1]["media"] == 9.0


def test_salvar_notas_sem_dados(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/notas/salvar",
        json={},
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400


def test_salvar_notas_com_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cursor = CursorFake(
        fetchone_results=[
            None,
            {"id": 5},
        ]
    )
    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/notas/salvar",
        json={
            "materia_id": 1,
            "alunos": [
                {"aluno_id": 1, "nota1": 8, "nota2": 9}
            ]
        },
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200


def test_professores_lista_coordenador(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 2, "nome": "Professor Teste"}
            ]
        ]
    )
    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/coordenador/professores-lista",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200


def test_turmas_por_professor_sem_professor(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/coordenador/turmas-por-professor",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400


def test_turmas_por_professor_com_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Turma A", "periodo": 1}
            ]
        ]
    )
    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/coordenador/turmas-por-professor?professor_id=2",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200


def test_materias_professor_turma_sem_parametros(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/coordenador/materias-por-professor-turma",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400


def test_materias_professor_turma_com_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Matemática"}
            ]
        ]
    )
    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/coordenador/materias-por-professor-turma?professor_id=2&turma_id=1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200


def test_salvar_presenca_sem_dados_extra(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/presenca/salvar",
        json={},
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400


def test_salvar_presenca_sem_permissao(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cursor = CursorFake(fetchone_results=[None])
    monkeypatch.setattr(presenca, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/presenca/salvar",
        json={
            "materia_id": 1,
            "turma_id": 1,
            "data_aula": "2026-06-06",
            "alunos": [
                {"aluno_id": 1, "presente": 1}
            ]
        },
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 403


def test_salvar_presenca_com_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cursor = CursorFake(
        fetchone_results=[
            {"ok": 1},
            None,
            {"id": 3},
        ]
    )
    monkeypatch.setattr(presenca, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/presenca/salvar",
        json={
            "materia_id": 1,
            "turma_id": 1,
            "data_aula": "2026-06-06",
            "justificativa": "Teste",
            "alunos": [
                {"aluno_id": 1, "presente": 1},
                {"aluno_id": 2, "presente": 0},
            ]
        },
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200