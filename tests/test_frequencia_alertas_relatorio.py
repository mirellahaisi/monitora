from backend.app import app
from backend import gerador_token
import backend.frequencia as frequencia


USUARIO_PROFESSOR = {
    "id": 2,
    "nome": "Professor Teste",
    "papel": "professor",
}

USUARIO_COORDENADOR = {
    "id": 1,
    "nome": "Coordenador Teste",
    "papel": "coordenador",
}


class CursorFake:
    def __init__(self, fetchall_results=None, fetchone_results=None):
        self.fetchall_results = fetchall_results or []
        self.fetchone_results = fetchone_results or []
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

    def cursor(self, dictionary=True):
        return self._cursor

    def close(self):
        pass


def autenticar_professor(monkeypatch):
    monkeypatch.setattr(frequencia, "validar_token", lambda token: USUARIO_PROFESSOR)
    monkeypatch.setattr(gerador_token, "validar_token", lambda token: USUARIO_PROFESSOR)


def autenticar_coordenador(monkeypatch):
    monkeypatch.setattr(frequencia, "validar_token", lambda token: USUARIO_COORDENADOR)
    monkeypatch.setattr(gerador_token, "validar_token", lambda token: USUARIO_COORDENADOR)


def test_relatorio_frequencia_txt(monkeypatch):
    cursor = CursorFake(
        fetchone_results=[
            {"nome": "Aluno Teste"},
            {"nome": "Turma A", "periodo": 1},
            {"nome": "Matemática"},
            {"total": 10, "presencas": 8, "faltas": 2},
        ]
    )

    monkeypatch.setattr(frequencia, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get("/frequencia/relatorio?aluno=1&materia=1&turma=1")

    texto = resposta.get_data(as_text=True)

    assert resposta.status_code == 200
    assert "RELATÓRIO DE FREQUÊNCIA" in texto
    assert "Aluno Teste" in texto
    assert resposta.mimetype == "text/plain"


def test_alertas_professor_sem_token():
    cliente = app.test_client()

    resposta = cliente.get("/api/frequencia/professor/alertas")

    assert resposta.status_code == 401
    assert resposta.get_json()["alertas"] == []


def test_alertas_professor_sem_permissao(monkeypatch):
    monkeypatch.setattr(frequencia, "validar_token", lambda token: {"id": 3, "papel": "aluno"})
    monkeypatch.setattr(gerador_token, "validar_token", lambda token: {"id": 3, "papel": "aluno"})

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/frequencia/professor/alertas",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 403
    assert resposta.get_json()["alertas"] == []


def test_alertas_professor_com_alertas(monkeypatch):
    autenticar_professor(monkeypatch)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "materia_id": 1,
                    "materia_nome": "Matemática",
                    "turma_id": 1,
                    "turma_nome": "Turma A",
                }
            ],
            [
                {
                    "id": 10,
                    "nome": "Aluno Baixa Frequência",
                    "total": 20,
                    "presencas": 5,
                    "faltas": 15,
                },
                {
                    "id": 11,
                    "nome": "Aluno Sem Aulas",
                    "total": 0,
                    "presencas": 0,
                    "faltas": 0,
                },
            ],
        ]
    )

    monkeypatch.setattr(frequencia, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/frequencia/professor/alertas",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert len(dados["alertas"]) == 1
    assert dados["alertas"][0]["nome"] == "Aluno Baixa Frequência"


def test_alertas_coordenador_sem_token():
    cliente = app.test_client()

    resposta = cliente.get("/api/frequencia/coordenador/alertas")

    assert resposta.status_code == 401
    assert resposta.get_json()["alertas"] == []


def test_alertas_coordenador_sem_permissao(monkeypatch):
    monkeypatch.setattr(frequencia, "validar_token", lambda token: {"id": 2, "papel": "professor"})
    monkeypatch.setattr(gerador_token, "validar_token", lambda token: {"id": 2, "papel": "professor"})

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/frequencia/coordenador/alertas",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 403
    assert resposta.get_json()["alertas"] == []


def test_alertas_coordenador_com_alertas(monkeypatch):
    autenticar_coordenador(monkeypatch)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 10,
                    "nome": "Aluno Crítico",
                    "materia_nome": "Banco de Dados",
                    "turma_nome": "Turma A",
                    "total": 20,
                    "presencas": 4,
                    "faltas": 16,
                },
                {
                    "id": 11,
                    "nome": "Aluno Regular",
                    "materia_nome": "Programação",
                    "turma_nome": "Turma B",
                    "total": 10,
                    "presencas": 9,
                    "faltas": 1,
                },
            ]
        ]
    )

    monkeypatch.setattr(frequencia, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/frequencia/coordenador/alertas",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert len(dados["alertas"]) >= 1
    assert dados["alertas"][0]["nome"] == "Aluno Crítico"