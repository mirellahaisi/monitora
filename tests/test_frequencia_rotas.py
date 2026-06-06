from backend.app import app
import backend.frequencia as frequencia


class CursorFake:
    def __init__(self):
        self.exec_count = 0

    def execute(self, *args, **kwargs):
        self.exec_count += 1

    def fetchall(self):
        if self.exec_count == 1:
            return [{"id": 1, "nome": "Matemática"}]

        if self.exec_count == 2:
            return [{"id": 1, "nome": "Turma A"}]

        if self.exec_count == 3:
            return [{"id": 1, "nome": "Aluno Teste"}]

        return []

    def fetchone(self):
        respostas = [
            {"nome": "Aluno Teste"},
            {"nome": "Matemática"},
            {"nome": "Turma A", "periodo": "Manhã"},
            {"total": 10, "presencas": 8, "faltas": 2},
        ]

        if self.exec_count <= len(respostas):
            return respostas[self.exec_count - 1]

        return None

    def close(self):
        pass


class ConexaoFake:
    def cursor(self, dictionary=True):
        return CursorFake()

    def close(self):
        pass


def test_materias_sem_token():
    cliente = app.test_client()

    resposta = cliente.get("/api/frequencia/materias")

    assert resposta.status_code == 200


def test_turmas_sem_materia():
    cliente = app.test_client()

    resposta = cliente.get("/api/frequencia/turmas")

    assert resposta.status_code == 200


def test_alunos_sem_turma():
    cliente = app.test_client()

    resposta = cliente.get("/api/frequencia/alunos")

    assert resposta.status_code == 200


def test_dados_sem_parametros():
    cliente = app.test_client()

    resposta = cliente.get("/api/frequencia/dados")

    assert resposta.status_code == 400


def test_dados_completos(monkeypatch):
    monkeypatch.setattr(
        frequencia,
        "criar_conexao",
        lambda: ConexaoFake()
    )

    cliente = app.test_client()

    resposta = cliente.get(
        "/api/frequencia/dados"
        "?aluno_id=1"
        "&materia_id=1"
        "&turma_id=1"
    )

    assert resposta.status_code == 200