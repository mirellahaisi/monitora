from backend.app import app
from backend import login
import backend.notas as notas
import backend.presenca as presenca


# ==========================
# USUÁRIOS FAKE
# ==========================

USUARIO_PROFESSOR = {
    "id": 1,
    "nome": "Professor Teste",
    "email": "prof@email.com",
    "papel": "professor",
    "papel_id": 2,
    "fk_papel_id": 2,
}

USUARIO_ALUNO = {
    "id": 10,
    "nome": "Aluno Teste",
    "email": "aluno@email.com",
    "papel": "aluno",
    "papel_id": 3,
    "fk_papel_id": 3,
}


# ==========================
# FAKES DE BANCO
# ==========================

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


def autenticar_professor(monkeypatch):
    monkeypatch.setattr(login, "validar_token", lambda token: USUARIO_PROFESSOR)


def autenticar_aluno(monkeypatch):
    monkeypatch.setattr(login, "validar_token", lambda token: USUARIO_ALUNO)


# ==========================
# TESTES - NOTAS
# ==========================

def test_notas_materias_professor(monkeypatch):
    autenticar_professor(monkeypatch)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Matemática"},
                {"id": 2, "nome": "Banco de Dados"},
            ]
        ]
    )

    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/materias",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert "materias" in dados
    assert dados["materias"][0]["nome"] == "Matemática"


def test_notas_materias_professor_com_curso(monkeypatch):
    autenticar_professor(monkeypatch)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Programação"},
            ]
        ]
    )

    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/materias?curso_id=1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["materias"][0]["nome"] == "Programação"


def test_notas_turmas_sem_materia(monkeypatch):
    autenticar_professor(monkeypatch)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/turmas",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400
    assert "message" in resposta.get_json()


def test_notas_turmas_com_materia(monkeypatch):
    autenticar_professor(monkeypatch)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Turma A", "periodo": 1},
                {"id": 2, "nome": "Turma B", "periodo": 2},
            ]
        ]
    )

    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/turmas?materia_id=1",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert "turmas" in dados
    assert dados["turmas"][0]["nome"] == "Turma A"


def test_notas_turmas_com_materia_e_curso(monkeypatch):
    autenticar_professor(monkeypatch)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Turma C", "periodo": 3},
            ]
        ]
    )

    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/turmas?materia_id=1&curso_id=2",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["turmas"][0]["nome"] == "Turma C"


def test_notas_alunos_sem_parametros(monkeypatch):
    autenticar_professor(monkeypatch)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/alunos",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400
    assert "message" in resposta.get_json()


def test_notas_alunos_com_media(monkeypatch):
    autenticar_professor(monkeypatch)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 1,
                    "nome": "Aluno B",
                    "nota1": 8,
                    "nota2": 10,
                },
                {
                    "id": 2,
                    "nome": "Aluno A",
                    "nota1": 6,
                    "nota2": None,
                },
            ]
        ]
    )

    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/alunos?materia_id=1&turma_id=1",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert "alunos" in dados
    assert dados["alunos"][0]["nome"] == "Aluno A"
    assert dados["alunos"][1]["media"] == 9.0


def test_minhas_notas_aluno(monkeypatch):
    autenticar_aluno(monkeypatch)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "materia_id": 1,
                    "materia_nome": "Banco de Dados",
                    "carga_horaria": 80,
                    "professores": "Professor Teste",
                    "nota1": 7,
                    "nota2": 9,
                },
                {
                    "materia_id": 2,
                    "materia_nome": "Programação",
                    "carga_horaria": 80,
                    "professores": "Professor Teste",
                    "nota1": None,
                    "nota2": None,
                },
            ]
        ]
    )

    monkeypatch.setattr(notas, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/notas/minhas-notas",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert "materias" in dados
    assert dados["materias"][0]["materia_nome"] == "Banco de Dados"
    assert dados["materias"][0]["media"] == 8.0


# ==========================
# TESTES - PRESENÇA
# ==========================

def test_presenca_materias(monkeypatch):
    autenticar_professor(monkeypatch)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Matemática"},
                {"id": 2, "nome": "Banco de Dados"},
            ]
        ]
    )

    monkeypatch.setattr(presenca, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/presenca/materias",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert "materias" in dados
    assert dados["materias"][0]["nome"] == "Matemática"


def test_presenca_materias_com_curso(monkeypatch):
    autenticar_professor(monkeypatch)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Programação"},
            ]
        ]
    )

    monkeypatch.setattr(presenca, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/presenca/materias?curso_id=1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["materias"][0]["nome"] == "Programação"


def test_presenca_turmas_sem_materia(monkeypatch):
    autenticar_professor(monkeypatch)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/presenca/turmas",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400
    assert "message" in resposta.get_json()


def test_presenca_turmas_com_materia(monkeypatch):
    autenticar_professor(monkeypatch)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Turma A", "periodo": 1},
            ]
        ]
    )

    monkeypatch.setattr(presenca, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/presenca/turmas?materia_id=1",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert "turmas" in dados
    assert dados["turmas"][0]["nome"] == "Turma A"


def test_presenca_turmas_com_materia_e_curso(monkeypatch):
    autenticar_professor(monkeypatch)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Turma C", "periodo": 3},
            ]
        ]
    )

    monkeypatch.setattr(presenca, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/presenca/turmas?materia_id=1&curso_id=2",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["turmas"][0]["nome"] == "Turma C"


def test_presenca_alunos_sem_parametros(monkeypatch):
    autenticar_professor(monkeypatch)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/presenca/alunos",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400
    assert "message" in resposta.get_json()


def test_presenca_alunos_com_sucesso(monkeypatch):
    autenticar_professor(monkeypatch)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Aluno B", "presente": None, "justificativa": None},
                {"id": 2, "nome": "Aluno A", "presente": 1, "justificativa": None},
            ]
        ]
    )

    monkeypatch.setattr(presenca, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/presenca/alunos?materia_id=1&turma_id=1&data_aula=2026-06-06",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert "alunos" in dados
    assert dados["alunos"][0]["nome"] == "Aluno A"


def test_salvar_presenca_sem_dados(monkeypatch):
    autenticar_professor(monkeypatch)

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/presenca",
        json={},
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code in [400, 404]