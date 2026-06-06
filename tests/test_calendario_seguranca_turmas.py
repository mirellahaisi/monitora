from datetime import datetime

from backend import calendario
from backend import gerador_token
from backend import seguranca
from backend import turmas


def test_calendario_estado_evento_comparavel():
    estado = calendario._estado_evento_comparavel(
        titulo=" Prova ",
        descricao=" Revisão ",
        data_inicio="2099-01-01T10:00",
        data_fim="2099-01-01T12:00",
        cor="",
        tipo="",
        pessoal=False,
        turma_id="1",
        materia_id="2",
        visibilidade="alunos",
    )

    assert estado["titulo"] == "Prova"
    assert estado["descricao"] == "Revisão"
    assert estado["cor"] == "#4caebe"
    assert estado["tipo"] == "evento"
    assert estado["fk_turma_id"] == 1
    assert estado["fk_materia_id"] == 2
    assert estado["visibilidade"] == "alunos"


def test_calendario_estado_evento_pessoal():
    estado = calendario._estado_evento_comparavel(
        titulo="Evento pessoal",
        descricao="",
        data_inicio="2099-01-01T10:00",
        data_fim="",
        cor="#fff",
        tipo="lembrete",
        pessoal=True,
        turma_id="1",
        materia_id="2",
        visibilidade="professores",
    )

    assert estado["pessoal"] is True
    assert estado["fk_turma_id"] is None
    assert estado["fk_materia_id"] is None
    assert estado["visibilidade"] == "todos"


def test_calendario_validar_datas_invalidas():
    assert calendario._validar_dados_evento("Evento", "data errada", None) is not None
    assert calendario._validar_dados_evento("Evento", "2099-01-01T10:00", "data errada") is not None
    assert calendario._validar_dados_evento("Evento", "2099-01-01T10:00", "2099-01-01T10:30") is not None
    assert calendario._validar_dados_evento("Evento", "2099-01-01T10:00", "2099-01-01T12:00") is None


def test_serializar_evento_coordenador_e_aluno():
    evento_coord = calendario._serializar_evento({
        "data_inicio": datetime(2099, 1, 1, 10, 0),
        "data_fim": None,
        "data_criacao": None,
        "pessoal": 1,
        "criador_papel": "coordenador",
        "criador_nome": "Maria",
    })

    evento_aluno = calendario._serializar_evento({
        "data_inicio": None,
        "data_fim": None,
        "data_criacao": None,
        "pessoal": 0,
        "criador_papel": "aluno",
        "criador_nome": "João",
    })

    assert evento_coord["criador_papel_label"] == "Coordenador – Maria"
    assert evento_aluno["criador_papel_label"] == "Aluno – João"


def test_gerador_token_base64_decode():
    texto = b"teste"
    codificado = gerador_token.base64url_encode(texto)

    assert gerador_token.base64url_decode(codificado) == texto


def test_seguranca_hash_invalido():
    assert seguranca.verificar_senha("123", "pbkdf2:invalido") is False


def test_turmas_buscar_proxima_letra():
    class CursorFake:
        def __init__(self):
            self.chamada = 0

        def execute(self, sql, params=None):
            self.chamada += 1

        def fetchall(self):
            if self.chamada == 1:
                return [
                    {"codigo": "ADS-2026-1-MA", "turma_letra": "A"}
                ]

            return []

    cursor = CursorFake()

    letra, codigo = turmas._buscar_proxima_letra_turma(
        cursor,
        curso_id=1,
        prefixo="ADS",
        periodo=1,
        ano=2026,
        semestre=1,
        turno="Manhã",
    )

    assert letra == "B"
    assert codigo == "ADS-2026-1-MB"