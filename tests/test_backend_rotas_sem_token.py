from backend.app import app


def test_paginas_html_carregam():
    cliente = app.test_client()

    rotas = [
        "/",
        "/login",
        "/inicio",
        "/perfil",
        "/gestao-usuarios",
        "/turmas",
        "/notas",
        "/frequencia",
        "/presenca",
        "/calendario",
        "/mensagens",
        "/cursos",
        "/materias",
    ]

    for rota in rotas:
        resposta = cliente.get(rota)
        assert resposta.status_code in [200, 302, 404, 500]


def test_rotas_api_sem_token_retornam_401():
    cliente = app.test_client()

    rotas = [
        "/api/usuarios/alunos",
        "/api/usuarios/professores",
        "/api/usuarios/coordenacao",
        "/api/cursos",
        "/api/materias",
        "/api/turmas",
        "/api/notas/materias",
        "/api/frequencia/todas-materias",
        "/api/presenca/materias",
        "/api/mensagens/recebidos",
        "/api/mensagens/enviados",
        "/api/calendario/eventos",
    ]

    for rota in rotas:
        resposta = cliente.get(rota)
        assert resposta.status_code in [401, 403, 404]


def test_login_sem_dados_retorna_400():
    cliente = app.test_client()

    resposta = cliente.post("/api/login", json={})

    assert resposta.status_code == 400
    assert "message" in resposta.get_json()


def test_login_legado_sem_dados_retorna_400():
    cliente = app.test_client()

    resposta = cliente.post("/api/login-legado", json={})

    assert resposta.status_code == 400
    assert "message" in resposta.get_json()


def test_usuario_logado_sem_token_retorna_401():
    cliente = app.test_client()

    resposta = cliente.get("/api/usuario-logado")

    assert resposta.status_code == 401
    assert "message" in resposta.get_json()


def test_usuario_logado_token_invalido_retorna_401():
    cliente = app.test_client()

    resposta = cliente.get(
        "/api/usuario-logado",
        headers={"Authorization": "Bearer token.invalido"}
    )

    assert resposta.status_code == 401
    assert "message" in resposta.get_json()