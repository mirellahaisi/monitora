"""
mensagens.py  –  Blueprint de Mensagens do Monitora+
Regras de negócio:
  - Aluno      → envia para: professor específico da turma (com matéria obrigatória)
                              OU coordenador específico (por nome)
  - Professor  → envia para: turma (alunos, com matéria opcional)
                              OU coordenador específico (por nome)
  - Coordenador→ envia para: turma inteira OU todos os professores OU todos (sem campo de turma)
"""
from datetime import datetime

from flask import Blueprint, jsonify, request

from conexao import criar_conexao
from gerador_token import validar_token

mensagens_bp = Blueprint("mensagens", __name__)


# ─────────────────────────────────────────
# Utilitários internos
# ─────────────────────────────────────────

def _usuario_do_token(req):
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return validar_token(auth.split(" ", 1)[1])


def _papel(payload):
    return str(payload.get("papel", "")).lower()


def _texto_limpo(valor):
    return str(valor or "").strip()


def _expandir_destinatarios(cursor, fk_turma_id, fk_materia_id, papel_destino, remetente_id, usuario_destino_id=None):
    """
    Retorna lista de IDs de usuários que devem receber a mensagem.
    usuario_destino_id: ID direto de um usuário (professor/coordenador específico)
    """
    ids = set()

    # Destino direto para um usuário específico (professor ou coordenador nomeado)
    if usuario_destino_id:
        ids.add(int(usuario_destino_id))
        return list(ids)

    base = """
        SELECT DISTINCT u.id
        FROM usuario u
        INNER JOIN papel p ON p.id = u.fk_papel_id
    """

    if fk_turma_id:
        if papel_destino in ("aluno", "todos"):
            cursor.execute(base + """
                INNER JOIN usuario_turma ut ON ut.fk_usuario_id = u.id
                WHERE ut.fk_turma_id = %s
                  AND LOWER(p.descricao) = 'aluno'
                  AND u.ativo = 1
                  AND u.id != %s
            """, (fk_turma_id, remetente_id))
            ids.update(r["id"] for r in cursor.fetchall())

        if papel_destino in ("professor", "todos"):
            filtro_materia = ""
            parametros_professores = [fk_turma_id, remetente_id]
            if fk_materia_id:
                filtro_materia = " AND ptm.fk_materia_id = %s"
                parametros_professores.insert(1, fk_materia_id)

            cursor.execute(f"""
                SELECT DISTINCT u.id
                FROM usuario u
                INNER JOIN professor_turma_materia ptm ON ptm.fk_usuario_id = u.id
                WHERE ptm.fk_turma_id = %s
                  {filtro_materia}
                  AND u.ativo = 1
                  AND u.id != %s
            """, tuple(parametros_professores))
            ids.update(r["id"] for r in cursor.fetchall())

    if papel_destino == "coordenador":
        cursor.execute(base + """
            WHERE LOWER(p.descricao) IN ('coordenador','admin','adm')
              AND u.ativo = 1
              AND u.id != %s
        """, (remetente_id,))
        ids.update(r["id"] for r in cursor.fetchall())

    return list(ids)


# ─────────────────────────────────────────
# ENVIAR AVISO  POST /api/mensagens
# ─────────────────────────────────────────

@mensagens_bp.post("/api/mensagens")
def enviar_mensagem():
    payload = _usuario_do_token(request)
    if not payload:
        return jsonify({"message": "Não autorizado."}), 401

    dados = request.get_json(silent=True) or {}
    titulo             = _texto_limpo(dados.get("titulo"))
    descricao          = _texto_limpo(dados.get("descricao"))
    turma_id           = dados.get("turma_id")           or None
    materia_id         = dados.get("materia_id")         or None
    papel_destino      = _texto_limpo(dados.get("papel_destino") or "todos").lower()
    usuario_destino_id = dados.get("usuario_destino_id") or None  # ID do professor/coord específico

    if not titulo or not descricao:
        return jsonify({"message": "Título e descrição são obrigatórios."}), 400

    if len(titulo) <= 3:
        return jsonify({"message": "O título deve ter mais de 3 caracteres."}), 400

    if len(descricao) <= 3:
        return jsonify({"message": "A mensagem deve ter mais de 3 caracteres."}), 400

    papel_rem    = _papel(payload)
    remetente_id = payload.get("id")
    if not remetente_id:
        return jsonify({"message": "Token inválido: sem ID de usuário. Faça login novamente."}), 401

    # ── Validação de permissão por papel ──
    permitido = False
    if papel_rem == "aluno":
        # Aluno envia para professor específico (com turma) ou coordenador específico
        if papel_destino == "coordenador" and usuario_destino_id:
            permitido = True
        elif papel_destino == "professor" and turma_id and usuario_destino_id:
            permitido = True
    elif papel_rem == "professor":
        if papel_destino == "coordenador" and usuario_destino_id:
            permitido = True
        elif papel_destino == "aluno" and turma_id:
            permitido = True
    elif papel_rem in ("coordenador", "admin", "adm"):
        permitido = True

    if not permitido:
        return jsonify({"message": "Você não tem permissão para este tipo de envio."}), 403

    conexao = criar_conexao()
    cursor  = conexao.cursor(dictionary=True)

    try:
        cursor.execute("""
            INSERT INTO mensagem
                (titulo, descricao, data_publicacao, fk_remetente_id,
                 fk_turma_id, fk_materia_id, papel_destino)
            VALUES (%s, %s, NOW(), %s, %s, %s, %s)
        """, (titulo, descricao, remetente_id, turma_id, materia_id, papel_destino))
        mensagem_id = cursor.lastrowid

        destinatarios = _expandir_destinatarios(
            cursor, turma_id, materia_id, papel_destino, remetente_id, usuario_destino_id
        )

        if destinatarios:
            vals = [(mensagem_id, uid) for uid in destinatarios]
            cursor.executemany("""
                INSERT IGNORE INTO mensagem_destinatario (fk_mensagem_id, fk_usuario_id)
                VALUES (%s, %s)
            """, vals)

        conexao.commit()
        return jsonify({
            "message": f"Mensagem enviada para {len(destinatarios)} destinatário(s).",
            "mensagem_id": mensagem_id,
            "total_destinatarios": len(destinatarios)
        }), 201

    except Exception as e:
        conexao.rollback()
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500
    finally:
        cursor.close()
        conexao.close()


# ─────────────────────────────────────────
# LISTAR AVISOS RECEBIDOS  GET /api/mensagens/recebidos
# ─────────────────────────────────────────

@mensagens_bp.get("/api/mensagens/recebidos")
def listar_recebidos():
    payload = _usuario_do_token(request)
    if not payload:
        return jsonify({"message": "Não autorizado."}), 401

    conexao = criar_conexao()
    cursor  = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.id,
            a.titulo,
            a.descricao,
            a.data_publicacao,
            a.papel_destino,
            u.nome          AS remetente_nome,
            p.descricao     AS remetente_papel,
            t.nome          AS turma_nome,
            m.nome          AS materia_nome,
            ad.lido,
            ad.data_leitura
        FROM mensagem_destinatario ad
        INNER JOIN mensagem   a ON a.id  = ad.fk_mensagem_id
        INNER JOIN usuario u ON u.id  = a.fk_remetente_id
        INNER JOIN papel   p ON p.id  = u.fk_papel_id
        LEFT  JOIN turma   t ON t.id  = a.fk_turma_id
        LEFT  JOIN materia m ON m.id  = a.fk_materia_id
        WHERE ad.fk_usuario_id = %s
          AND a.ativo = 1
        ORDER BY a.data_publicacao DESC
        LIMIT 100
    """, (payload.get("id"),))

    mensagens = cursor.fetchall()

    for av in mensagens:
        for k in ("data_publicacao", "data_leitura"):
            if av.get(k):
                av[k] = av[k].strftime("%Y-%m-%d %H:%M:%S")

    cursor.close()
    conexao.close()
    return jsonify({"mensagens": mensagens})


# ─────────────────────────────────────────
# LISTAR AVISOS ENVIADOS  GET /api/mensagens/enviados
# ─────────────────────────────────────────

@mensagens_bp.get("/api/mensagens/enviados")
def listar_enviados():
    payload = _usuario_do_token(request)
    if not payload:
        return jsonify({"message": "Não autorizado."}), 401

    conexao = criar_conexao()
    cursor  = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.id,
            a.titulo,
            a.descricao,
            a.data_publicacao,
            a.papel_destino,
            t.nome  AS turma_nome,
            m.nome  AS materia_nome,
            COUNT(DISTINCT ad.fk_usuario_id)                AS total_destinatarios,
            COALESCE(SUM(ad.lido = 1), 0)                   AS total_lidos,
            CASE
                WHEN COUNT(DISTINCT dest.id) = 1 THEN MAX(dest.nome)
                ELSE NULL
            END                                             AS destinatario_nome,
            CASE
                WHEN COUNT(DISTINCT dest.id) = 1 THEN MAX(p_dest.descricao)
                ELSE NULL
            END                                             AS destinatario_papel
        FROM mensagem a
        LEFT JOIN turma   t  ON t.id = a.fk_turma_id
        LEFT JOIN materia m  ON m.id = a.fk_materia_id
        LEFT JOIN mensagem_destinatario ad ON ad.fk_mensagem_id = a.id
        LEFT JOIN usuario dest ON dest.id = ad.fk_usuario_id
        LEFT JOIN papel p_dest ON p_dest.id = dest.fk_papel_id
        WHERE a.fk_remetente_id = %s
          AND a.ativo = 1
        GROUP BY
            a.id,
            a.titulo,
            a.descricao,
            a.data_publicacao,
            a.papel_destino,
            t.nome,
            m.nome
        ORDER BY a.data_publicacao DESC
        LIMIT 100
    """, (payload.get("id"),))

    mensagens = cursor.fetchall()

    for av in mensagens:
        if av.get("data_publicacao"):
            av["data_publicacao"] = av["data_publicacao"].strftime("%Y-%m-%d %H:%M:%S")

    cursor.close()
    conexao.close()
    return jsonify({"mensagens": mensagens})


# ─────────────────────────────────────────
# MARCAR COMO LIDO  PATCH /api/mensagens/<id>/lido
# ─────────────────────────────────────────

@mensagens_bp.patch("/api/mensagens/<int:mensagem_id>/lido")
def marcar_lido(mensagem_id):
    payload = _usuario_do_token(request)
    if not payload:
        return jsonify({"message": "Não autorizado."}), 401

    conexao = criar_conexao()
    cursor  = conexao.cursor()

    cursor.execute("""
        UPDATE mensagem_destinatario
        SET lido = 1, data_leitura = NOW()
        WHERE fk_mensagem_id = %s AND fk_usuario_id = %s AND lido = 0
    """, (mensagem_id, payload.get("id")))

    conexao.commit()
    affected = cursor.rowcount
    cursor.close()
    conexao.close()
    return jsonify({"message": "Marcado como lido.", "affected": affected})


# ─────────────────────────────────────────
# CONTAGEM NÃO LIDOS  GET /api/mensagens/nao-lidos
# ─────────────────────────────────────────

@mensagens_bp.get("/api/mensagens/nao-lidos")
def nao_lidos():
    payload = _usuario_do_token(request)
    if not payload:
        return jsonify({"message": "Não autorizado."}), 401

    conexao = criar_conexao()
    cursor  = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM mensagem_destinatario ad
        INNER JOIN mensagem a ON a.id = ad.fk_mensagem_id
        WHERE ad.fk_usuario_id = %s AND ad.lido = 0 AND a.ativo = 1
    """, (payload.get("id"),))

    row = cursor.fetchone()
    cursor.close()
    conexao.close()
    return jsonify({"nao_lidos": row["total"] if row else 0})


# ─────────────────────────────────────────
# OPÇÕES DE ENVIO  GET /api/mensagens/opcoes
# ─────────────────────────────────────────

@mensagens_bp.get("/api/mensagens/opcoes")
def opcoes_envio():
    payload = _usuario_do_token(request)
    if not payload:
        return jsonify({"message": "Não autorizado."}), 401

    papel_rem = _papel(payload)
    conexao   = criar_conexao()
    cursor    = conexao.cursor(dictionary=True)

    turmas   = []
    destinos = []

    if papel_rem == "aluno":
        # Turmas nas quais o aluno está matriculado
        cursor.execute("""
            SELECT t.id, t.nome, t.periodo
            FROM turma t
            INNER JOIN usuario_turma ut ON ut.fk_turma_id = t.id
            WHERE ut.fk_usuario_id = %s AND t.ativo = 1
            ORDER BY t.nome
        """, (payload.get("id"),))
        turmas = cursor.fetchall()

        destinos = [
            {"valor": "professor",   "label": "Professor"},
            {"valor": "coordenador", "label": "Coordenador"},
        ]

    elif papel_rem == "professor":
        # Turmas onde o professor leciona
        cursor.execute("""
            SELECT DISTINCT t.id, t.nome, t.periodo
            FROM turma t
            INNER JOIN professor_turma_materia ptm ON ptm.fk_turma_id = t.id
            WHERE ptm.fk_usuario_id = %s AND t.ativo = 1
            ORDER BY t.nome
        """, (payload.get("id"),))
        turmas = cursor.fetchall()

        destinos = [
            {"valor": "aluno",       "label": "Turma"},
            {"valor": "coordenador", "label": "Coordenador"},
        ]

    else:  # coordenador / admin
        destinos = [
            {"valor": "turma",      "label": "Turma"},
            {"valor": "professor",  "label": "Professor"},
            {"valor": "todos",      "label": "Todos"},
        ]

    cursor.close()
    conexao.close()
    return jsonify({"turmas": turmas, "destinos": destinos})


# ─────────────────────────────────────────
# MATÉRIAS DE UMA TURMA  GET /api/mensagens/materias?turma_id=X
# ─────────────────────────────────────────

@mensagens_bp.get("/api/mensagens/materias")
def materias_da_turma():
    payload = _usuario_do_token(request)
    if not payload:
        return jsonify({"message": "Não autorizado."}), 401

    turma_id  = request.args.get("turma_id")
    if not turma_id:
        return jsonify([])

    conexao = criar_conexao()
    cursor  = conexao.cursor(dictionary=True)

    papel_rem = _papel(payload)

    if papel_rem == "professor":
        # Só as matérias que o professor leciona nessa turma
        cursor.execute("""
            SELECT m.id, m.nome
            FROM materia m
            INNER JOIN professor_turma_materia ptm ON ptm.fk_materia_id = m.id
            WHERE ptm.fk_turma_id = %s
              AND ptm.fk_usuario_id = %s
              AND m.ativo = 1
            ORDER BY m.nome
        """, (turma_id, payload.get("id")))
    elif papel_rem == "aluno":
        # Matérias da turma ligadas a um professor específico
        professor_id = request.args.get("professor_id")
        if professor_id:
            cursor.execute("""
                SELECT m.id, m.nome
                FROM materia m
                INNER JOIN professor_turma_materia ptm ON ptm.fk_materia_id = m.id
                WHERE ptm.fk_turma_id = %s
                  AND ptm.fk_usuario_id = %s
                  AND m.ativo = 1
                ORDER BY m.nome
            """, (turma_id, professor_id))
        else:
            cursor.execute("""
                SELECT m.id, m.nome
                FROM materia m
                INNER JOIN materias_turma mt ON mt.fk_materia_id = m.id
                WHERE mt.fk_turma_id = %s AND m.ativo = 1
                ORDER BY m.nome
            """, (turma_id,))
    else:
        cursor.execute("""
            SELECT m.id, m.nome
            FROM materia m
            INNER JOIN materias_turma mt ON mt.fk_materia_id = m.id
            WHERE mt.fk_turma_id = %s AND m.ativo = 1
            ORDER BY m.nome
        """, (turma_id,))

    materias = cursor.fetchall()
    cursor.close()
    conexao.close()
    return jsonify(materias)


# ─────────────────────────────────────────
# PROFESSORES DE UMA TURMA  GET /api/mensagens/professores?turma_id=X
# ─────────────────────────────────────────

@mensagens_bp.get("/api/mensagens/professores")
def professores_da_turma():
    payload = _usuario_do_token(request)
    if not payload:
        return jsonify({"message": "Não autorizado."}), 401

    turma_id = request.args.get("turma_id")
    if not turma_id:
        return jsonify([])

    conexao = criar_conexao()
    cursor  = conexao.cursor(dictionary=True)

    # Retorna professores distintos que lecionam nessa turma
    cursor.execute("""
        SELECT DISTINCT u.id, u.nome
        FROM usuario u
        INNER JOIN professor_turma_materia ptm ON ptm.fk_usuario_id = u.id
        WHERE ptm.fk_turma_id = %s AND u.ativo = 1
        ORDER BY u.nome
    """, (turma_id,))

    professores = cursor.fetchall()
    cursor.close()
    conexao.close()
    return jsonify(professores)


# ─────────────────────────────────────────
# TODOS OS PROFESSORES  GET /api/mensagens/todos-professores
# (para coordenador enviar para professor específico)
# ─────────────────────────────────────────

@mensagens_bp.get("/api/mensagens/todos-professores")
def todos_professores():
    payload = _usuario_do_token(request)
    if not payload:
        return jsonify({"message": "Não autorizado."}), 401

    papel_rem = _papel(payload)
    if papel_rem not in ("coordenador", "admin", "adm"):
        return jsonify({"message": "Acesso negado."}), 403

    conexao = criar_conexao()
    cursor  = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT u.id, u.nome
        FROM usuario u
        INNER JOIN papel p ON p.id = u.fk_papel_id
        WHERE LOWER(p.descricao) = 'professor' AND u.ativo = 1
        ORDER BY u.nome
    """)

    professores = cursor.fetchall()
    cursor.close()
    conexao.close()
    return jsonify(professores)


# ─────────────────────────────────────────
# TODAS AS TURMAS  GET /api/mensagens/todas-turmas
# (para coordenador)
# ─────────────────────────────────────────

@mensagens_bp.get("/api/mensagens/todas-turmas")
def todas_turmas():
    payload = _usuario_do_token(request)
    if not payload:
        return jsonify({"message": "Não autorizado."}), 401

    papel_rem = _papel(payload)
    if papel_rem not in ("coordenador", "admin", "adm"):
        return jsonify({"message": "Acesso negado."}), 403

    conexao = criar_conexao()
    cursor  = conexao.cursor(dictionary=True)

    cursor.execute("SELECT id, nome, periodo FROM turma WHERE ativo = 1 ORDER BY nome")
    turmas = cursor.fetchall()
    cursor.close()
    conexao.close()
    return jsonify(turmas)


# ─────────────────────────────────────────
# TODOS OS COORDENADORES  GET /api/mensagens/coordenadores
# ─────────────────────────────────────────

@mensagens_bp.get("/api/mensagens/coordenadores")
def todos_coordenadores():
    payload = _usuario_do_token(request)
    if not payload:
        return jsonify({"message": "Não autorizado."}), 401

    conexao = criar_conexao()
    cursor  = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT u.id, u.nome
        FROM usuario u
        INNER JOIN papel p ON p.id = u.fk_papel_id
        WHERE LOWER(p.descricao) IN ('coordenador','admin','adm')
          AND u.ativo = 1
          AND u.id != %s
        ORDER BY u.nome
    """, (payload.get("id"),))

    coordenadores = cursor.fetchall()
    cursor.close()
    conexao.close()
    return jsonify(coordenadores)
