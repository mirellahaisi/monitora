from datetime import datetime, timedelta

from backend.app import app
from backend import login
import backend.calendario as calendario


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

USUARIO_ALUNO = {
    "id": 3,
    "nome": "Aluno Teste",
    "email": "aluno@email.com",
    "papel": "aluno",
    "papel_id": 3,
}


class CursorFake:
    def __init__(self, fetchall_results=None, fetchone_results=None, rowcount=1):
        self.fetchall_results = fetchall_results or []
        self.fetchone_results = fetchone_results or []
        self.rowcount = rowcount
        self.lastrowid = 77
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


def data_futura():
    return (datetime.now() + timedelta(days=10)).replace(second=0, microsecond=0)


def test_helpers_calendario():
    assert calendario._texto_limpo("  Evento  ") == "Evento"
    assert calendario._valor_bool("true") is True
    assert calendario._valor_bool("sim") is True
    assert calendario._valor_bool("false") is False
    assert calendario._normalizar_id("10") == 10
    assert calendario._normalizar_id(None) is None
    assert calendario._normalizar_visibilidade("alunos") == "alunos"
    assert calendario._normalizar_visibilidade("invalido") == "todos"
    assert calendario._parse_datetime_local("2099-01-01T10:00") is not None
    assert calendario._parse_datetime_local("data errada") is None


def test_serializar_evento():
    evento = calendario._serializar_evento({
        "id": 1,
        "titulo": "Prova",
        "data_inicio": datetime(2099, 1, 1, 10, 0),
        "data_fim": datetime(2099, 1, 1, 11, 0),
        "data_criacao": datetime(2099, 1, 1, 9, 0),
        "pessoal": 0,
        "criador_papel": "professor",
        "criador_nome": "João",
    })

    assert evento["pessoal"] is False
    assert evento["criador_papel_label"] == "Professor – João"
    assert evento["data_inicio"].startswith("2099-01-01")


def test_validar_evento_titulo_curto():
    erro = calendario._validar_dados_evento("Oi", "2099-01-01T10:00", None)
    assert erro is not None


def test_listar_eventos_coordenador(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 1,
                    "titulo": "Reunião",
                    "descricao": "Reunião pedagógica",
                    "data_inicio": datetime(2099, 1, 1, 10, 0),
                    "data_fim": datetime(2099, 1, 1, 11, 0),
                    "data_criacao": datetime(2099, 1, 1, 9, 0),
                    "cor": "#4caebe",
                    "tipo": "evento",
                    "pessoal": 0,
                    "visibilidade": "todos",
                    "fk_criador_id": 1,
                    "criador_nome": "Coordenador Teste",
                    "criador_papel": "coordenador",
                    "fk_turma_id": None,
                    "turma_nome": None,
                    "fk_materia_id": None,
                    "materia_nome": None,
                }
            ]
        ]
    )

    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/calendario",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["eventos"][0]["titulo"] == "Reunião"


def test_listar_eventos_professor(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 2,
                    "titulo": "Aula",
                    "descricao": "Aula normal",
                    "data_inicio": datetime(2099, 1, 2, 10, 0),
                    "data_fim": None,
                    "data_criacao": None,
                    "cor": "#4caebe",
                    "tipo": "evento",
                    "pessoal": 0,
                    "visibilidade": "professores",
                    "fk_criador_id": 2,
                    "criador_nome": "Professor Teste",
                    "criador_papel": "professor",
                    "fk_turma_id": 1,
                    "turma_nome": "Turma A",
                    "fk_materia_id": 1,
                    "materia_nome": "Matemática",
                }
            ]
        ]
    )

    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/calendario?mes=1&ano=2099",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["eventos"][0]["titulo"] == "Aula"


def test_listar_eventos_aluno(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cursor = CursorFake(
        fetchall_results=[
            [
                {
                    "id": 3,
                    "titulo": "Estudo",
                    "descricao": "Revisão",
                    "data_inicio": datetime(2099, 1, 3, 10, 0),
                    "data_fim": None,
                    "data_criacao": None,
                    "cor": "#4caebe",
                    "tipo": "evento",
                    "pessoal": 1,
                    "visibilidade": "todos",
                    "fk_criador_id": 3,
                    "criador_nome": "Aluno Teste",
                    "criador_papel": "aluno",
                    "fk_turma_id": None,
                    "turma_nome": None,
                    "fk_materia_id": None,
                    "materia_nome": None,
                }
            ]
        ]
    )

    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/calendario",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["eventos"][0]["pessoal"] is True


def test_criar_evento_sem_titulo(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/calendario",
        json={"data_inicio": "2099-01-01T10:00"},
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400


def test_criar_evento_aluno_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cursor = CursorFake()
    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/calendario",
        json={
            "titulo": "Estudar",
            "descricao": "Revisar conteúdo",
            "data_inicio": "2099-01-01T10:00",
            "data_fim": "2099-01-01T12:00",
            "cor": "#ffffff",
            "tipo": "evento",
        },
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 201
    assert resposta.get_json()["id"] == 77


def test_criar_evento_professor_sem_turma(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/calendario",
        json={
            "titulo": "Aula",
            "data_inicio": "2099-01-01T10:00",
            "pessoal": False,
        },
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 400


def test_criar_evento_professor_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cursor = CursorFake(
        fetchone_results=[
            {"cnt": 1},
            {"cnt": 1},
        ]
    )

    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/calendario",
        json={
            "titulo": "Aula",
            "descricao": "Aula de banco",
            "data_inicio": "2099-01-01T10:00",
            "data_fim": "2099-01-01T12:00",
            "fk_turma_id": 1,
            "fk_materia_id": 1,
            "pessoal": False,
        },
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 201


def test_criar_evento_coordenador_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake()
    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.post(
        "/api/calendario",
        json={
            "titulo": "Conselho",
            "descricao": "Reunião",
            "data_inicio": "2099-01-01T10:00",
            "data_fim": "2099-01-01T12:00",
            "visibilidade": "professores",
            "pessoal": False,
        },
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 201


def test_deletar_evento_nao_encontrado(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(fetchone_results=[None])
    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.delete(
        "/api/calendario/999",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 404


def test_deletar_evento_sem_permissao(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(fetchone_results=[{"fk_criador_id": 99}])
    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.delete(
        "/api/calendario/1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 403


def test_deletar_evento_sucesso(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(fetchone_results=[{"fk_criador_id": 1}])
    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.delete(
        "/api/calendario/1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200


def test_opcoes_aluno(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/calendario/opcoes",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["turmas"] == []


def test_opcoes_professor(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Turma A", "periodo": 1}
            ]
        ]
    )

    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/calendario/opcoes",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["turmas"][0]["nome"] == "Turma A"


def test_opcoes_coordenador(monkeypatch):
    autenticar(monkeypatch, USUARIO_COORDENADOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Turma Geral", "periodo": 1}
            ]
        ]
    )

    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/calendario/opcoes",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["turmas"][0]["nome"] == "Turma Geral"


def test_materias_por_turma_como_aluno_negado(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/calendario/materias/1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 403


def test_materias_por_turma_professor(monkeypatch):
    autenticar(monkeypatch, USUARIO_PROFESSOR)

    cursor = CursorFake(
        fetchall_results=[
            [
                {"id": 1, "nome": "Matemática"}
            ]
        ]
    )

    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.get(
        "/api/calendario/materias/1",
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["materias"][0]["nome"] == "Matemática"


def test_atualizar_evento_nao_encontrado(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cursor = CursorFake(fetchone_results=[None])
    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.put(
        "/api/calendario/999",
        json={"titulo": "Novo título"},
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 404


def test_atualizar_evento_sem_permissao(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cursor = CursorFake(
        fetchone_results=[
            {
                "id": 1,
                "fk_criador_id": 99,
                "titulo": "Evento",
                "descricao": "Desc",
                "data_inicio": datetime(2099, 1, 1, 10, 0),
                "data_fim": None,
                "cor": "#4caebe",
                "tipo": "evento",
                "fk_turma_id": None,
                "fk_materia_id": None,
                "pessoal": True,
                "visibilidade": "todos",
            }
        ]
    )
    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.put(
        "/api/calendario/1",
        json={"titulo": "Novo título"},
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 403


def test_atualizar_evento_sucesso_aluno(monkeypatch):
    autenticar(monkeypatch, USUARIO_ALUNO)

    cursor = CursorFake(
        fetchone_results=[
            {
                "id": 1,
                "fk_criador_id": 3,
                "titulo": "Evento antigo",
                "descricao": "Desc",
                "data_inicio": datetime(2099, 1, 1, 10, 0),
                "data_fim": None,
                "cor": "#4caebe",
                "tipo": "evento",
                "fk_turma_id": None,
                "fk_materia_id": None,
                "pessoal": True,
                "visibilidade": "todos",
            }
        ]
    )
    monkeypatch.setattr(calendario, "criar_conexao", lambda: ConexaoFake(cursor))

    cliente = app.test_client()
    resposta = cliente.put(
        "/api/calendario/1",
        json={
            "titulo": "Evento novo",
            "data_inicio": "2099-01-01T10:00",
        },
        headers={"Authorization": "Bearer token"}
    )

    assert resposta.status_code == 200