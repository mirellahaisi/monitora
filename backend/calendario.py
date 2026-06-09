from flask import Blueprint, jsonify, render_template, request
from datetime import datetime, timedelta
import mysql.connector

from .conexao import criar_conexao
from .login import token_obrigatorio, papel_obrigatorio

calendario_bp = Blueprint("calendario", __name__)


# ── Tela ──────────────────────────────────────────────────────────────────────

@calendario_bp.get("/calendario")
def tela_calendario():
    return render_template("pages/calendario.html", active_page="calendario")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _serializar_evento(ev):
    """Converte datetimes e Decimals para tipos JSON-serializáveis."""
    ev = dict(ev)
    for campo in ("data_inicio", "data_fim", "data_criacao"):
        if ev.get(campo):
            ev[campo] = ev[campo].isoformat()
    ev["pessoal"] = bool(ev.get("pessoal", False))
    papel_raw = str(ev.get("criador_papel") or "").lower()
    nome      = ev.get("criador_nome") or ""
    if papel_raw in ("admin", "adm", "coordenador"):
        ev["criador_papel_label"] = f"Coordenador – {nome}"
    elif papel_raw == "professor":
        ev["criador_papel_label"] = f"Professor – {nome}"
    else:
        ev["criador_papel_label"] = f"Aluno – {nome}"
    return ev


def _texto_limpo(valor):
    return str(valor or "").strip()


def _valor_bool(valor):
    if isinstance(valor, bool):
        return valor

    if isinstance(valor, str):
        return valor.strip().lower() in ("1", "true", "sim", "yes", "on")

    return bool(valor)


def _normalizar_id(valor):
    if valor in (None, ""):
        return None

    try:
        return int(valor)
    except (TypeError, ValueError):
        return valor


def _normalizar_visibilidade(valor):
    visibilidade = _texto_limpo(valor).lower() or "todos"
    if visibilidade not in ("todos", "alunos", "professores"):
        return "todos"
    return visibilidade


def _parse_datetime_local(valor):
    if valor in (None, ""):
        return None

    if isinstance(valor, datetime):
        return valor.replace(second=0, microsecond=0)

    try:
        return datetime.fromisoformat(str(valor).strip()).replace(second=0, microsecond=0)
    except (TypeError, ValueError):
        return None


def _agora_no_minuto():
    return datetime.now().replace(second=0, microsecond=0)


def _data_comparacao(valor):
    data = _parse_datetime_local(valor)
    return data.isoformat(timespec="minutes") if data else None


def _estado_evento_comparavel(
    titulo,
    descricao,
    data_inicio,
    data_fim,
    cor,
    tipo,
    pessoal,
    turma_id,
    materia_id,
    visibilidade
):
    eh_pessoal = bool(pessoal)
    return {
        "titulo": _texto_limpo(titulo),
        "descricao": _texto_limpo(descricao),
        "data_inicio": _data_comparacao(data_inicio),
        "data_fim": _data_comparacao(data_fim),
        "cor": _texto_limpo(cor) or "#4caebe",
        "tipo": _texto_limpo(tipo) or "evento",
        "pessoal": eh_pessoal,
        "fk_turma_id": None if eh_pessoal else _normalizar_id(turma_id),
        "fk_materia_id": None if eh_pessoal else _normalizar_id(materia_id),
        "visibilidade": "todos" if eh_pessoal else _normalizar_visibilidade(visibilidade),
    }


def _validar_dados_evento(titulo, data_inicio, data_fim):
    titulo_limpo = _texto_limpo(titulo)
    if len(titulo_limpo) < 3:
        return "O título deve ter no mínimo 3 caracteres."

    inicio = _parse_datetime_local(data_inicio)
    if not inicio:
        return "Informe uma data e hora de início válida."

    agora = _agora_no_minuto()
    if inicio < agora:
        return "A data e hora de início não podem estar no passado."

    if data_fim not in (None, ""):
        fim = _parse_datetime_local(data_fim)
        if not fim:
            return "Informe uma data e hora de fim válida."

        if fim < agora:
            return "A data e hora de fim não podem estar no passado."

        if fim < inicio + timedelta(hours=1):
            return "A data e hora de fim deve ter pelo menos 1 hora de diferença do início."

    return None


# ── GET /api/calendario ───────────────────────────────────────────────────────
#
# Regras de visibilidade:
#
#   Aluno
#     • Eventos de TURMA com visibilidade 'todos' ou 'alunos'
#       vinculados a uma das turmas do aluno
#     • Eventos GLOBAIS (sem turma) com visibilidade 'todos' ou 'alunos'
#     • Eventos PESSOAIS criados pelo próprio aluno (pessoal = TRUE)
#
#   Professor
#     • Eventos que ele mesmo criou (qualquer visibilidade)
#     • Eventos de coordenador/admin com visibilidade 'todos' ou 'professores'
#
#   Coordenador / Admin
#     • Todos os eventos ativos

@calendario_bp.get("/api/calendario")
@token_obrigatorio
def listar_eventos(usuario):
    mes   = request.args.get("mes",  type=int)
    ano   = request.args.get("ano",  type=int)
    papel = str(usuario.get("papel", "")).lower()

    filtro_data = ""
    params_data = []
    if mes and ano:
        filtro_data = "AND MONTH(ec.data_inicio) = %s AND YEAR(ec.data_inicio) = %s"
        params_data = [mes, ano]

    conexao = cursor = None
    try:
        conexao = criar_conexao()
        cursor  = conexao.cursor(dictionary=True)

        # ── Coordenador / Admin ────────────────────────────────────────────
        if papel in ("admin", "adm", "coordenador"):
            cursor.execute(f"""
                SELECT
                    ec.id, ec.titulo, ec.descricao,
                    ec.data_inicio, ec.data_fim,
                    ec.cor, ec.tipo, ec.pessoal, ec.visibilidade,
                    ec.fk_criador_id,   u.nome  AS criador_nome,
                    p.descricao         AS criador_papel,
                    ec.fk_turma_id,     t.nome  AS turma_nome,
                    ec.fk_materia_id,   m.nome  AS materia_nome
                FROM evento_calendario ec
                INNER JOIN usuario u ON u.id = ec.fk_criador_id
                INNER JOIN papel   p ON p.id = u.fk_papel_id
                LEFT  JOIN turma   t ON t.id  = ec.fk_turma_id
                LEFT  JOIN materia m ON m.id  = ec.fk_materia_id
                WHERE ec.ativo = 1
                  AND ec.fk_criador_id = %s
                {filtro_data}
                ORDER BY ec.data_inicio
            """, [usuario["id"]] + params_data)

        # ── Professor ─────────────────────────────────────────────────────
        elif papel == "professor":
            cursor.execute(f"""
                SELECT DISTINCT
                    ec.id, ec.titulo, ec.descricao,
                    ec.data_inicio, ec.data_fim,
                    ec.cor, ec.tipo, ec.pessoal, ec.visibilidade,
                    ec.fk_criador_id,   u.nome  AS criador_nome,
                    p.descricao         AS criador_papel,
                    ec.fk_turma_id,     t.nome  AS turma_nome,
                    ec.fk_materia_id,   m.nome  AS materia_nome
                FROM evento_calendario ec
                INNER JOIN usuario u ON u.id = ec.fk_criador_id
                INNER JOIN papel   p ON p.id = u.fk_papel_id
                LEFT  JOIN turma   t ON t.id  = ec.fk_turma_id
                LEFT  JOIN materia m ON m.id  = ec.fk_materia_id
                WHERE ec.ativo = 1
                  AND (
                      ec.fk_criador_id = %s
                      OR
                      (
                          ec.pessoal = FALSE
                          AND LOWER(p.descricao) IN ('admin','adm','coordenador')
                          AND ec.visibilidade IN ('todos','professores')
                      )
                  )
                {filtro_data}
                ORDER BY ec.data_inicio
            """, [usuario["id"]] + params_data)

        # ── Aluno ─────────────────────────────────────────────────────────
        else:
            cursor.execute(f"""
                SELECT DISTINCT
                    ec.id, ec.titulo, ec.descricao,
                    ec.data_inicio, ec.data_fim,
                    ec.cor, ec.tipo, ec.pessoal, ec.visibilidade,
                    ec.fk_criador_id,   u.nome  AS criador_nome,
                    p.descricao         AS criador_papel,
                    ec.fk_turma_id,     t.nome  AS turma_nome,
                    ec.fk_materia_id,   m.nome  AS materia_nome
                FROM evento_calendario ec
                INNER JOIN usuario u ON u.id = ec.fk_criador_id
                INNER JOIN papel   p ON p.id = u.fk_papel_id
                LEFT  JOIN turma   t ON t.id  = ec.fk_turma_id
                LEFT  JOIN materia m ON m.id  = ec.fk_materia_id
                LEFT  JOIN usuario_turma ut
                        ON ut.fk_turma_id  = ec.fk_turma_id
                       AND ut.fk_usuario_id = %s
                WHERE ec.ativo = 1
                  AND (
                    (ec.pessoal = TRUE AND ec.fk_criador_id = %s)

                    OR (ec.pessoal = FALSE
                        AND ec.visibilidade IN ('todos','alunos')
                        AND (
                            ec.fk_turma_id IS NULL
                            OR ut.fk_usuario_id IS NOT NULL
                        )
                    )
                )
                {filtro_data}
                ORDER BY ec.data_inicio
            """, [usuario["id"], usuario["id"]] + params_data)

        eventos = [_serializar_evento(ev) for ev in cursor.fetchall()]
        return jsonify({"eventos": eventos}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar eventos.", "erro": str(erro)}), 500
    finally:
        if cursor:  cursor.close()
        if conexao and conexao.is_connected(): conexao.close()


# ── POST /api/calendario ──────────────────────────────────────────────────────
#
# Regras por papel:
#
#   Aluno       → sempre pessoal=TRUE, sem turma/matéria
#   Professor   → pessoal=FALSE obrigatório escolher turma (das suas);
#                 matéria opcional (apenas as da turma selecionada);
#                 visibilidade sempre 'alunos' — sem opção global
#   Coordenador → pessoal=FALSE, escolhe turma (ou global) E visibilidade;
#                 SEM campo matéria (materia_id sempre NULL)

@calendario_bp.post("/api/calendario")
@token_obrigatorio
def criar_evento(usuario):
    dados = request.get_json(silent=True) or {}
    papel = str(usuario.get("papel", "")).lower()

    titulo      = _texto_limpo(dados.get("titulo"))
    descricao   = _texto_limpo(dados.get("descricao")) or None
    data_inicio = dados.get("data_inicio")
    data_fim    = dados.get("data_fim") or None
    cor         = _texto_limpo(dados.get("cor")) or "#4caebe"
    tipo        = _texto_limpo(dados.get("tipo")) or "evento"
    mensagem_validacao = _validar_dados_evento(titulo, data_inicio, data_fim) if titulo and data_inicio else None
    if mensagem_validacao:
        return jsonify({"message": mensagem_validacao}), 400

    if not titulo or not data_inicio:
        return jsonify({"message": "Título e data de início são obrigatórios."}), 400

    # ── Aluno: evento sempre pessoal ──────────────────────────────────────
    if papel == "aluno":
        turma_id     = None
        materia_id   = None
        pessoal      = True
        visibilidade = "todos"

    # ── Professor: obrigatório escolher turma; sem opção global ──────────
    elif papel == "professor":
        pessoal_req = _valor_bool(dados.get("pessoal", False))
        if pessoal_req:
            turma_id     = None
            materia_id   = None
            pessoal      = True
            visibilidade = "todos"
        else:
            turma_id = dados.get("fk_turma_id") or None
            if not turma_id:
                return jsonify({"message": "Professor deve selecionar uma turma."}), 400
            materia_id   = dados.get("fk_materia_id") or None
            if not materia_id:
                return jsonify({"message": "Professor deve selecionar uma matéria."}), 400
            pessoal      = False
            visibilidade = "alunos"   # professor nunca cria evento global

    # ── Coordenador / Admin: turma opcional, SEM matéria ─────────────────
    elif papel in ("admin", "adm", "coordenador"):
        pessoal_req = _valor_bool(dados.get("pessoal", False))
        if pessoal_req:
            turma_id     = None
            materia_id   = None
            pessoal      = True
            visibilidade = "todos"
        else:
            turma_id     = dados.get("fk_turma_id") or None
            materia_id   = None   # coordenador não vincula matéria
            pessoal      = False
            visibilidade = _normalizar_visibilidade(dados.get("visibilidade", "todos"))

    else:
        return jsonify({"message": "Papel não autorizado a criar eventos."}), 403

    conexao = cursor = None
    try:
        conexao = criar_conexao()
        cursor  = conexao.cursor(dictionary=True)

        # Professor: valida que a turma realmente pertence a ele
        if papel == "professor" and not pessoal and turma_id:
            cursor.execute("""
                SELECT COUNT(*) AS cnt
                FROM professor_turma_materia ptm
                INNER JOIN turma t ON t.id = ptm.fk_turma_id
                WHERE ptm.fk_usuario_id = %s
                  AND ptm.fk_turma_id = %s
                  AND t.ativo = 1
            """, (usuario["id"], turma_id))
            row = cursor.fetchone()
            if not row or row["cnt"] == 0:
                return jsonify({"message": "Você não leciona nessa turma."}), 403

        # Professor: se informou matéria, valida que pertence à turma selecionada
        if papel == "professor" and not pessoal and materia_id and turma_id:
            cursor.execute("""
                SELECT COUNT(*) AS cnt
                FROM professor_turma_materia ptm
                WHERE ptm.fk_usuario_id = %s
                  AND ptm.fk_materia_id = %s
                  AND ptm.fk_turma_id = %s
            """, (usuario["id"], materia_id, turma_id))
            row = cursor.fetchone()
            if not row or row["cnt"] == 0:
                return jsonify({"message": "Você não leciona essa matéria nessa turma."}), 403

        cursor.execute("""
            INSERT INTO evento_calendario
                (titulo, descricao, data_inicio, data_fim, cor, tipo,
                 fk_criador_id, fk_turma_id, fk_materia_id, pessoal, visibilidade)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (titulo, descricao, _parse_datetime_local(data_inicio), _parse_datetime_local(data_fim), cor, tipo,
              usuario["id"], turma_id, materia_id, pessoal, visibilidade))

        conexao.commit()
        return jsonify({"message": "Evento criado com sucesso.", "id": cursor.lastrowid}), 201

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao criar evento.", "erro": str(erro)}), 500
    finally:
        if cursor:  cursor.close()
        if conexao and conexao.is_connected(): conexao.close()


# ── PUT /api/calendario/<id> ──────────────────────────────────────────────────
# Apenas o criador do evento pode editá-lo (qualquer papel).

@calendario_bp.put("/api/calendario/<int:evento_id>")
@token_obrigatorio
def atualizar_evento(usuario, evento_id):
    dados = request.get_json(silent=True) or {}
    papel = str(usuario.get("papel", "")).lower()
    return _atualizar_evento_impl(usuario, evento_id, dados, papel)

    conexao = cursor = None
    try:
        conexao = criar_conexao()
        cursor  = conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT fk_criador_id, pessoal FROM evento_calendario WHERE id = %s AND ativo = 1",
            (evento_id,)
        )
        ev = cursor.fetchone()
        if not ev:
            return jsonify({"message": "Evento não encontrado."}), 404

        if ev["fk_criador_id"] != usuario["id"]:
            return jsonify({"message": "Sem permissão para editar este evento."}), 403

        campos  = []
        valores = []

        for campo in ("titulo", "descricao", "data_inicio", "data_fim", "cor", "tipo"):
            if campo in dados:
                campos.append(f"{campo} = %s")
                valores.append(dados[campo] or None)

        if papel != "aluno" and "pessoal" in dados:
            novo_pessoal = bool(dados["pessoal"])
            campos.append("pessoal = %s")
            valores.append(novo_pessoal)
            if novo_pessoal:
                campos += ["fk_turma_id = NULL", "fk_materia_id = NULL"]

        pessoal_atualizado = bool(dados.get("pessoal", ev["pessoal"]))

        # Professor: pode alterar turma/matéria, mas matéria deve ser da turma
        if papel == "professor" and not pessoal_atualizado:
            if "fk_turma_id" in dados:
                campos.append("fk_turma_id = %s")
                valores.append(dados["fk_turma_id"] or None)
            # matéria sempre atualizada junto com turma
            if "fk_materia_id" in dados:
                campos.append("fk_materia_id = %s")
                valores.append(dados["fk_materia_id"] or None)

        # Coordenador: pode alterar turma e visibilidade, mas nunca matéria
        if papel in ("admin", "adm", "coordenador") and not pessoal_atualizado:
            if "fk_turma_id" in dados:
                campos.append("fk_turma_id = %s")
                valores.append(dados["fk_turma_id"] or None)
            # força materia_id = NULL para coordenador
            campos.append("fk_materia_id = NULL")
            if "visibilidade" in dados:
                vis = dados["visibilidade"]
                if vis in ("todos", "alunos", "professores"):
                    campos.append("visibilidade = %s")
                    valores.append(vis)

        if not campos:
            return jsonify({"message": "Nenhum campo para atualizar."}), 400

        valores.append(evento_id)
        cursor2 = conexao.cursor()
        cursor2.execute(
            f"UPDATE evento_calendario SET {', '.join(campos)} WHERE id = %s",
            valores
        )
        conexao.commit()
        cursor2.close()

        return jsonify({"message": "Evento atualizado com sucesso."}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao atualizar evento.", "erro": str(erro)}), 500
    finally:
        if cursor:  cursor.close()
        if conexao and conexao.is_connected(): conexao.close()


# ── DELETE /api/calendario/<id> ───────────────────────────────────────────────
# Apenas o criador do evento pode excluí-lo (qualquer papel).

@calendario_bp.delete("/api/calendario/<int:evento_id>")
@token_obrigatorio
def deletar_evento(usuario, evento_id):
    conexao = cursor = None
    try:
        conexao = criar_conexao()
        cursor  = conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT fk_criador_id FROM evento_calendario WHERE id = %s AND ativo = 1",
            (evento_id,)
        )
        ev = cursor.fetchone()
        if not ev:
            return jsonify({"message": "Evento não encontrado."}), 404

        if ev["fk_criador_id"] != usuario["id"]:
            return jsonify({"message": "Sem permissão para excluir este evento."}), 403

        cursor2 = conexao.cursor()
        cursor2.execute(
            "UPDATE evento_calendario SET ativo = 0 WHERE id = %s", (evento_id,)
        )
        conexao.commit()
        cursor2.close()

        return jsonify({"message": "Evento removido com sucesso."}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao remover evento.", "erro": str(erro)}), 500
    finally:
        if cursor:  cursor.close()
        if conexao and conexao.is_connected(): conexao.close()


# ── GET /api/calendario/opcoes ────────────────────────────────────────────────
# Turmas para o formulário (matérias são carregadas dinamicamente por turma).
#
#   Coordenador → todas as turmas ativas; SEM matérias
#   Professor   → apenas as turmas em que ele leciona; SEM matérias globais
#                 (matérias são buscadas via /api/calendario/materias/<turma_id>)

@calendario_bp.get("/api/calendario/opcoes")
@token_obrigatorio
def opcoes_formulario(usuario):
    papel = str(usuario.get("papel", "")).lower()

    if papel == "aluno":
        return jsonify({"turmas": [], "materias": []}), 200

    conexao = cursor = None
    try:
        conexao = criar_conexao()
        cursor  = conexao.cursor(dictionary=True)

        if papel in ("admin", "adm", "coordenador"):
            # Coordenador vê todas as turmas, sem matérias
            cursor.execute(
                "SELECT id, nome, periodo FROM turma WHERE ativo = 1 ORDER BY nome"
            )
            turmas = cursor.fetchall()
            materias = []   # coordenador não usa campo de matéria

        else:
            # Professor: apenas suas turmas
            cursor.execute("""
                SELECT DISTINCT t.id, t.nome, t.periodo
                FROM turma t
                INNER JOIN professor_turma_materia ptm ON ptm.fk_turma_id = t.id
                WHERE ptm.fk_usuario_id = %s AND t.ativo = 1
                ORDER BY t.nome
            """, (usuario["id"],))
            turmas = cursor.fetchall()
            materias = []   # matérias carregadas dinamicamente via /materias/<turma_id>

        return jsonify({"turmas": turmas, "materias": materias}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar opções.", "erro": str(erro)}), 500
    finally:
        if cursor:  cursor.close()
        if conexao and conexao.is_connected(): conexao.close()


# ── GET /api/calendario/materias/<turma_id> ───────────────────────────────────
# Retorna as matérias que o professor logado leciona na turma informada.
# Usado pelo frontend para popular dinamicamente o select de matéria
# após o professor selecionar uma turma.

@calendario_bp.get("/api/calendario/materias/<int:turma_id>")
@token_obrigatorio
def materias_por_turma(usuario, turma_id):
    papel = str(usuario.get("papel", "")).lower()

    if papel != "professor":
        return jsonify({"message": "Apenas professores usam este endpoint."}), 403

    conexao = cursor = None
    try:
        conexao = criar_conexao()
        cursor  = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT m.id, m.nome
            FROM materia m
            INNER JOIN professor_turma_materia ptm ON ptm.fk_materia_id = m.id
            WHERE ptm.fk_usuario_id = %s
              AND ptm.fk_turma_id = %s
              AND m.ativo = 1
            ORDER BY m.nome
        """, (usuario["id"], turma_id))

        materias = cursor.fetchall()
        return jsonify({"materias": materias}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar matérias.", "erro": str(erro)}), 500
    finally:
        if cursor:  cursor.close()
        if conexao and conexao.is_connected(): conexao.close()


def _atualizar_evento_impl(usuario, evento_id, dados, papel):
    conexao = cursor = None
    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id, fk_criador_id, titulo, descricao, data_inicio, data_fim,
                cor, tipo, fk_turma_id, fk_materia_id, pessoal, visibilidade
            FROM evento_calendario
            WHERE id = %s AND ativo = 1
            LIMIT 1
        """, (evento_id,))
        ev = cursor.fetchone()
        if not ev:
            return jsonify({"message": "Evento não encontrado."}), 404

        if ev["fk_criador_id"] != usuario["id"]:
            return jsonify({"message": "Sem permissão para editar este evento."}), 403

        titulo = _texto_limpo(dados.get("titulo")) if "titulo" in dados else _texto_limpo(ev.get("titulo"))
        descricao = _texto_limpo(dados.get("descricao")) if "descricao" in dados else _texto_limpo(ev.get("descricao"))
        data_inicio = dados.get("data_inicio") if "data_inicio" in dados else ev.get("data_inicio")
        data_fim = dados.get("data_fim") if "data_fim" in dados else ev.get("data_fim")
        cor = _texto_limpo(dados.get("cor")) if "cor" in dados else (_texto_limpo(ev.get("cor")) or "#4caebe")
        tipo = _texto_limpo(dados.get("tipo")) if "tipo" in dados else (_texto_limpo(ev.get("tipo")) or "evento")

        if not titulo or not data_inicio:
            return jsonify({"message": "Título e data de início são obrigatórios."}), 400

        mensagem_validacao = _validar_dados_evento(titulo, data_inicio, data_fim)
        if mensagem_validacao:
            return jsonify({"message": mensagem_validacao}), 400

        visibilidade_atual = _normalizar_visibilidade(ev.get("visibilidade"))

        if papel == "aluno":
            pessoal = True
            turma_id = None
            materia_id = None
            visibilidade = visibilidade_atual or "todos"
        elif papel == "professor":
            pessoal = _valor_bool(dados["pessoal"]) if "pessoal" in dados else bool(ev.get("pessoal"))
            if pessoal:
                turma_id = None
                materia_id = None
                visibilidade = "todos"
            else:
                turma_id = dados.get("fk_turma_id") if "fk_turma_id" in dados else ev.get("fk_turma_id")
                materia_id = dados.get("fk_materia_id") if "fk_materia_id" in dados else ev.get("fk_materia_id")
                if not turma_id:
                    return jsonify({"message": "Professor deve selecionar uma turma."}), 400
                if not materia_id:
                    return jsonify({"message": "Professor deve selecionar uma matéria."}), 400
                visibilidade = "alunos" if bool(ev.get("pessoal")) else (visibilidade_atual or "alunos")
        elif papel in ("admin", "adm", "coordenador"):
            pessoal = _valor_bool(dados["pessoal"]) if "pessoal" in dados else bool(ev.get("pessoal"))
            if pessoal:
                turma_id = None
                materia_id = None
                visibilidade = "todos"
            else:
                turma_id = dados.get("fk_turma_id") if "fk_turma_id" in dados else ev.get("fk_turma_id")
                materia_id = None
                visibilidade = _normalizar_visibilidade(dados.get("visibilidade", ev.get("visibilidade")))
        else:
            return jsonify({"message": "Papel não autorizado a editar eventos."}), 403

        estado_atual = _estado_evento_comparavel(
            ev.get("titulo"),
            ev.get("descricao"),
            ev.get("data_inicio"),
            ev.get("data_fim"),
            ev.get("cor"),
            ev.get("tipo"),
            ev.get("pessoal"),
            ev.get("fk_turma_id"),
            ev.get("fk_materia_id"),
            ev.get("visibilidade"),
        )
        estado_novo = _estado_evento_comparavel(
            titulo,
            descricao,
            data_inicio,
            data_fim,
            cor,
            tipo,
            pessoal,
            turma_id,
            materia_id,
            visibilidade,
        )

        if estado_atual == estado_novo:
            return jsonify({"message": "Nenhum dado foi atualizado."}), 400

        if papel == "professor" and not pessoal and turma_id:
            cursor.execute("""
                SELECT COUNT(*) AS cnt
                FROM professor_turma_materia ptm
                INNER JOIN turma t ON t.id = ptm.fk_turma_id
                WHERE ptm.fk_usuario_id = %s
                  AND ptm.fk_turma_id = %s
                  AND t.ativo = 1
            """, (usuario["id"], turma_id))
            row = cursor.fetchone()
            if not row or row["cnt"] == 0:
                return jsonify({"message": "Você não leciona nessa turma."}), 403

        if papel == "professor" and not pessoal and materia_id and turma_id:
            cursor.execute("""
                SELECT COUNT(*) AS cnt
                FROM professor_turma_materia ptm
                WHERE ptm.fk_usuario_id = %s
                  AND ptm.fk_materia_id = %s
                  AND ptm.fk_turma_id = %s
            """, (usuario["id"], materia_id, turma_id))
            row = cursor.fetchone()
            if not row or row["cnt"] == 0:
                return jsonify({"message": "Você não leciona essa matéria nessa turma."}), 403

        cursor.execute("""
            UPDATE evento_calendario
            SET titulo = %s,
                descricao = %s,
                data_inicio = %s,
                data_fim = %s,
                cor = %s,
                tipo = %s,
                fk_turma_id = %s,
                fk_materia_id = %s,
                pessoal = %s,
                visibilidade = %s
            WHERE id = %s
        """, (
            titulo,
            descricao or None,
            _parse_datetime_local(data_inicio),
            _parse_datetime_local(data_fim),
            cor,
            tipo,
            turma_id,
            materia_id,
            pessoal,
            visibilidade,
            evento_id
        ))
        conexao.commit()

        return jsonify({"message": "Evento atualizado com sucesso."}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao atualizar evento.", "erro": str(erro)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()
