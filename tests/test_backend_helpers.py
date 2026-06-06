from datetime import date, datetime, timedelta
import time

from backend import seguranca
from backend import gerador_token
from backend import login
from backend import gestao_usuarios
from backend import turmas
from backend import materias
from backend import cursos


def test_seguranca_senhas():
    senha = "123456"
    hash_senha = seguranca.gerar_hash_senha(senha)

    assert seguranca.senha_esta_hash(hash_senha) is True
    assert seguranca.verificar_senha(senha, hash_senha) is True
    assert seguranca.verificar_senha("errada", hash_senha) is False
    assert seguranca.verificar_senha("abc", "abc") is True
    assert seguranca.verificar_senha("abc", "") is False
    assert seguranca.senha_precisa_upgrade("abc") is True
    assert seguranca.senha_precisa_upgrade(hash_senha) is False


def test_senha_padrao_data_nascimento():
    assert seguranca.senha_padrao_data_nascimento("2005-08-02") == "020805"
    assert seguranca.senha_padrao_data_nascimento(date(2005, 8, 2)) == "020805"
    assert seguranca.senha_padrao_data_nascimento(datetime(2005, 8, 2)) == "020805"


def test_gerador_token_valido_e_invalido():
    usuario = {
        "id": 1,
        "nome": "Mirella",
        "email": "mirella@email.com",
        "papel": "aluno",
        "fk_papel_id": 3,
    }

    token, payload = gerador_token.gerar_token(usuario)

    assert payload["nome"] == "Mirella"
    assert gerador_token.validar_token(token)["email"] == "mirella@email.com"
    assert gerador_token.validar_token("token.invalido") is None
    assert gerador_token.validar_token(token + "x") is None


def test_login_helpers():
    assert login.somente_numeros("123.456.789-00") == "12345678900"
    assert login.email_valido("teste@email.com") is True
    assert login.email_valido("email-invalido") is False

    data = login.converter_data_iso("2000-01-10")
    assert data == date(2000, 1, 10)
    assert login.converter_data_iso("errado") is None

    assert login.idade_minima_valida(date.today() - timedelta(days=365 * 20)) is True
    assert login.idade_minima_valida(date.today()) is False


def test_gestao_usuarios_formatacao_validacao():
    assert gestao_usuarios.somente_numeros("(41) 99999-8888") == "41999998888"
    assert gestao_usuarios._formatar_cpf("12345678909") == "123.456.789-09"
    assert gestao_usuarios._formatar_telefone("41999998888") == "(41) 99999-8888"
    assert gestao_usuarios._formatar_telefone("4133334444") == "(41) 3333-4444"

    assert gestao_usuarios._email_valido("teste@email.com") is True
    assert gestao_usuarios._email_valido("emailerrado") is False

    assert gestao_usuarios._telefone_valido("41999998888") is True
    assert gestao_usuarios._telefone_valido("123") is False

    assert gestao_usuarios._papel_por_fk(1) == "coordenador"
    assert gestao_usuarios._papel_por_fk(2) == "professor"
    assert gestao_usuarios._papel_por_fk(3) == "aluno"


def test_gestao_usuarios_data_e_idade():
    nascimento = gestao_usuarios._parse_data_nascimento("2000-01-01")

    assert nascimento == date(2000, 1, 1)
    assert gestao_usuarios._parse_data_nascimento("data errada") is None
    assert gestao_usuarios._calcular_idade(nascimento) >= 20
    assert gestao_usuarios._idade_minima_atingida(nascimento, "aluno") is True


def test_turmas_helpers():
    assert turmas._normalizar_turno(" Manhã ") == "Manhã"
    assert turmas._sigla_turno("Noite") == "N"
    assert turmas._normalizar_letra_turma("a") == "A"
    assert turmas._normalizar_letra_turma("ab") is None
    assert turmas._montar_nome_turma("ADS", 2026, 1, "Noite", "A") == "ADS 2026.1 - Noite"
    assert turmas._montar_nome_turma("ADS", 2026, 1, "Noite", "B") == "ADS 2026.1 - Noite B"
    assert turmas._extrair_letra_do_codigo("ADS-2026-1-NA", "ADS", 2026, 1, "N") == "A"


def test_normalizar_ativo_materias_e_cursos():
    for modulo in (materias, cursos):
        assert modulo.normalizar_ativo(True) is True
        assert modulo.normalizar_ativo(False) is False
        assert modulo.normalizar_ativo("true") is True
        assert modulo.normalizar_ativo("sim") is True
        assert modulo.normalizar_ativo("false") is False
        assert modulo.normalizar_ativo("não") is False
        assert modulo.normalizar_ativo(1) is True
        assert modulo.normalizar_ativo(0) is False