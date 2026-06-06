from datetime import datetime

from backend.app import app
from backend import mensagens


USUARIO_ALUNO = {
    "id": 3,
    "nome": "Aluno Teste",
    "papel": "aluno",
}

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
    def __init__(self, fetchone_results=None, fetchall_results=None, rowcount=1):
        self.fetchone_results = fetchone_results or []
        self.fetchall_results = fetchall_results or []
        self.rowcount = rowcount
        self.lastrowid = 55
        self.executed = []
        self.executemany_calls = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def executemany(self, sql, values):
        self.executemany_calls.append((sql, values))

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
    monkeypatch.setattr(mensagens, "validar_token", lambda token: usuario)


def test_recebidos_com_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 1,
                    "titulo": "Aviso",
                    "descricao": "Mensagem teste",
                    "data_publicacao": datetime(2026, 1, 1, 10, 0, 0),
                    "papel_destino": "aluno",
                    "remetente_nome": "Professor Teste",
                    "remetente_papel": "professor",
                    "turma_nome": "SI 2026.1",
                    "materia_nome": "Banco de Dados",
                    "lido": 0,
                    "data_leitura": None,
                }
            ]
        ]
    )

    monkeypatch.setattr(mensagens, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/recebidos",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["mensagens"][0]["titulo"] == "Aviso"
    assert dados["mensagens"][0]["data_publicacao"] == "2026-01-01 10:00:00"


def test_enviados_com_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 1,
                    "titulo": "Trabalho",
                    "descricao": "Entrega amanhã",
                    "data_publicacao": datetime(2026, 1, 2, 9, 0, 0),
                    "papel_destino": "aluno",
                    "turma_nome": "SI 2026.1",
                    "materia_nome": "Programação",
                    "total_destinatarios": 10,
                    "total_lidos": 5,
                    "destinatario_nome": None,
                    "destinatario_papel": None,
                }
            ]
        ]
    )

    monkeypatch.setattr(mensagens, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/enviados",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["mensagens"][0]["titulo"] == "Trabalho"


def test_marcar_mensagem_como_lida(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cursor = CursorFake(rowcount=1)
    monkeypatch.setattr(mensagens, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.patch(
        "/api/mensagens/1/lido",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["affected"] == 1


def test_contar_nao_lidos(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cursor = CursorFake(fetchone_results=[{"total": 3}])
    monkeypatch.setattr(mensagens, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/nao-lidos",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["nao_lidos"] == 3


def test_opcoes_envio_aluno(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "SI 2026.1", "periodo": 1}
            ]
        ]
    )

    monkeypatch.setattr(mensagens, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/opcoes",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["destinos"][0]["valor"] == "professor"


def test_opcoes_envio_professor(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "SI 2026.1", "periodo": 1}
            ]
        ]
    )

    monkeypatch.setattr(mensagens, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/opcoes",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["destinos"][0]["valor"] == "aluno"


def test_opcoes_envio_coordenador(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake()
    monkeypatch.setattr(mensagens, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/opcoes",
        headers={"Authorization": "Bearer token"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["destinos"][0]["valor"] == "turma"


def test_materias_sem_turma_retorna_lista_vazia(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/materias",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json() == []


def test_materias_da_turma(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Banco de Dados"}
            ]
        ]
    )

    monkeypatch.setattr(mensagens, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/materias?turma_id=1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()[0]["nome"] == "Banco de Dados"


def test_professores_sem_turma_retorna_lista_vazia(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/professores",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json() == []


def test_professores_da_turma(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 2, "nome": "Professor Teste"}
            ]
        ]
    )

    monkeypatch.setattr(mensagens, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/professores?turma_id=1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()[0]["nome"] == "Professor Teste"


def test_todos_professores_como_coordenador(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 2, "nome": "Professor Teste"}
            ]
        ]
    )

    monkeypatch.setattr(mensagens, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/todos-professores",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()[0]["nome"] == "Professor Teste"


def test_todos_professores_como_aluno_negado(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/todos-professores",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 403


def test_todas_turmas_como_coordenador(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "SI 2026.1", "periodo": 1}
            ]
        ]
    )

    monkeypatch.setattr(mensagens, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/todas-turmas",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()[0]["nome"] == "SI 2026.1"


def test_todos_coordenadores(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Coordenador Teste"}
            ]
        ]
    )

    monkeypatch.setattr(mensagens, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/mensagens/coordenadores",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()[0]["nome"] == "Coordenador Teste"


def test_enviar_mensagem_sem_titulo(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/mensagens",
        json={
            "titulo": "",
            "descricao": "Mensagem válida",
            "papel_destino": "aluno",
            "turma_id": 1,
        },
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400


def test_enviar_mensagem_sem_permissao(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/mensagens",
        json={
            "titulo": "Aviso válido",
            "descricao": "Mensagem válida",
            "papel_destino": "aluno",
        },
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 403


def test_enviar_mensagem_com_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 3},
                {"id": 4},
            ]
        ]
    )

    monkeypatch.setattr(mensagens, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/mensagens",
        json={
            "titulo": "Aviso válido",
            "descricao": "Mensagem válida",
            "papel_destino": "coordenador",
        },
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 201
    assert "mensagem_id" in resposta.get_json()