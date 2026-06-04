from flask import Blueprint, render_template, request, Response, jsonify

from conexao import criar_conexao

frequencia_bp = Blueprint("frequencia", __name__)


# ========================
# ROTA DE TELA
# ========================

@frequencia_bp.route("/frequencia")
def frequencia():
    return render_template(
        "pages/frequencia.html",
        active_page="frequencia",
    )


# ========================
# APIS PARA OS SELECTS DINÂMICOS
# ========================

@frequencia_bp.get("/api/frequencia/materias")
def api_todas_materias():
    """Retorna todas as matérias ativas (primeiro select)."""
    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, nome
        FROM materia
        WHERE ativo = 1
        ORDER BY nome
    """)

    materias = cursor.fetchall()
    cursor.close()
    conexao.close()

    return jsonify(materias)


@frequencia_bp.get("/api/frequencia/turmas")
def api_turmas_por_materia():
    """Retorna as turmas que possuem a matéria selecionada."""
    materia_id = request.args.get("materia_id")

    if not materia_id:
        return jsonify([])

    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT t.id, t.nome, t.periodo
        FROM turma t
        INNER JOIN materias_turma mt ON mt.fk_turma_id = t.id
        WHERE mt.fk_materia_id = %s AND t.ativo = 1
        ORDER BY t.periodo, t.nome
    """, (materia_id,))

    turmas = cursor.fetchall()
    cursor.close()
    conexao.close()

    return jsonify(turmas)


@frequencia_bp.get("/api/frequencia/alunos")
def api_alunos_por_turma():
    """Retorna os alunos da turma selecionada."""
    turma_id = request.args.get("turma_id")

    if not turma_id:
        return jsonify([])

    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT u.id, u.nome
        FROM usuario u
        INNER JOIN usuario_turma ut ON ut.fk_usuario_id = u.id
        INNER JOIN papel p ON p.id = u.fk_papel_id
        WHERE ut.fk_turma_id = %s
          AND LOWER(p.descricao) = 'aluno'
          AND u.ativo = 1
        ORDER BY u.nome
    """, (turma_id,))

    alunos = cursor.fetchall()
    cursor.close()
    conexao.close()

    return jsonify(alunos)


@frequencia_bp.get("/api/frequencia/dados")
def api_dados_frequencia():
    """Retorna os dados de frequência de um aluno em uma matéria/turma."""
    aluno_id   = request.args.get("aluno_id")
    materia_id = request.args.get("materia_id")
    turma_id   = request.args.get("turma_id")

    if not aluno_id or not materia_id or not turma_id:
        return jsonify({"error": "Parâmetros insuficientes"}), 400

    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    # Nome do aluno
    cursor.execute("SELECT nome FROM usuario WHERE id = %s", (aluno_id,))
    aluno_row = cursor.fetchone()

    # Nome da matéria
    cursor.execute("SELECT nome FROM materia WHERE id = %s", (materia_id,))
    materia_row = cursor.fetchone()

    # Nome e período da turma
    cursor.execute("SELECT nome, periodo FROM turma WHERE id = %s", (turma_id,))
    turma_row = cursor.fetchone()

    # Dados de frequência
    cursor.execute("""
        SELECT
            COUNT(id)                       AS total,
            COALESCE(SUM(presente = 1), 0)  AS presencas,
            COALESCE(SUM(presente = 0), 0)  AS faltas
        FROM frequencia
        WHERE fk_usuario_id = %s AND fk_materia_id = %s
    """, (aluno_id, materia_id))

    freq = cursor.fetchone()

    cursor.close()
    conexao.close()

    total    = freq["total"]    if freq else 0
    presencas = freq["presencas"] if freq else 0
    faltas   = freq["faltas"]   if freq else 0

    # Cálculo: começa em 100%, cada falta desconta 2%
    pct_raw = max(0, 100 - (faltas * 2))

    turma_label  = f"{turma_row['nome']} — {turma_row['periodo']}º Período" if turma_row else "—"
    materia_label = materia_row["nome"] if materia_row else "—"
    aluno_nome   = aluno_row["nome"]    if aluno_row  else "—"

    return jsonify({
        "nome":         aluno_nome,
        "materia":      materia_label,
        "turma":        turma_label,
        "total":        total,
        "presencas":    presencas,
        "faltas":       faltas,
        "presenca":     f"{pct_raw}%",
        "presenca_raw": pct_raw,
    })


# ========================
# API PARA ALUNO VER A PRÓPRIA FREQUÊNCIA (papel = 3)
# ========================

@frequencia_bp.get("/api/frequencia/dados-proprios")
def api_dados_proprios():
    """
    Retorna a frequência do aluno logado em todas as suas matérias.
    Usado pela view de papel=3 (aluno).
    Parâmetro: aluno_id (vindo do JWT decodificado no front-end).
    """
    aluno_id = request.args.get("aluno_id")

    if not aluno_id:
        return jsonify({"error": "Parâmetro aluno_id ausente"}), 400

    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    # Nome do aluno
    cursor.execute("SELECT nome FROM usuario WHERE id = %s AND ativo = 1", (aluno_id,))
    aluno_row = cursor.fetchone()

    if not aluno_row:
        cursor.close()
        conexao.close()
        return jsonify({"error": "Aluno não encontrado"}), 404

    # Busca todas as matérias do aluno (via turmas em que está matriculado)
    cursor.execute("""
        SELECT DISTINCT
            m.id   AS materia_id,
            m.nome AS materia_nome,
            t.id   AS turma_id,
            t.nome AS turma_nome,
            t.periodo
        FROM usuario_turma ut
        INNER JOIN turma t          ON t.id  = ut.fk_turma_id
        INNER JOIN materias_turma mt ON mt.fk_turma_id = t.id
        INNER JOIN materia m        ON m.id  = mt.fk_materia_id
        WHERE ut.fk_usuario_id = %s
          AND t.ativo = 1
          AND m.ativo = 1
        ORDER BY m.nome
    """, (aluno_id,))

    materias_turmas = cursor.fetchall()

    resultado = []
    for row in materias_turmas:
        cursor.execute("""
            SELECT
                COUNT(id)                       AS total,
                COALESCE(SUM(presente = 1), 0)  AS presencas,
                COALESCE(SUM(presente = 0), 0)  AS faltas
            FROM frequencia
            WHERE fk_usuario_id = %s AND fk_materia_id = %s
        """, (aluno_id, row["materia_id"]))

        freq = cursor.fetchone()

        total     = freq["total"]     if freq else 0
        presencas = freq["presencas"] if freq else 0
        faltas    = freq["faltas"]    if freq else 0
        pct_raw   = max(0, 100 - (faltas * 2))

        resultado.append({
            "materia_id":   row["materia_id"],
            "materia":      row["materia_nome"],
            "turma":        f"{row['turma_nome']} — {row['periodo']}º Período",
            "turma_id":     row["turma_id"],
            "total":        total,
            "presencas":    presencas,
            "faltas":       faltas,
            "presenca":     f"{pct_raw}%",
            "presenca_raw": pct_raw,
        })

    cursor.close()
    conexao.close()

    return jsonify({
        "nome":     aluno_row["nome"],
        "materias": resultado,
    })


# ========================
# RESUMO DO ALUNO LOGADO (para o dashboard)
# ========================

@frequencia_bp.get("/api/frequencia/aluno/resumo")
def api_resumo_aluno():
    """
    Retorna a frequência média (%) do aluno logado em todas as suas matérias.
    Usado no dashboard do aluno (stat de frequência).
    """
    from gerador_token import validar_token

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Não autorizado"}), 401

    payload = validar_token(auth.split(" ", 1)[1])
    if not payload:
        return jsonify({"error": "Token inválido"}), 401

    aluno_id = payload.get("id")

    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    try:
        # Busca todas as matérias do aluno
        cursor.execute("""
            SELECT DISTINCT m.id AS materia_id
            FROM usuario_turma ut
            INNER JOIN turma t          ON t.id  = ut.fk_turma_id
            INNER JOIN materias_turma mt ON mt.fk_turma_id = t.id
            INNER JOIN materia m        ON m.id  = mt.fk_materia_id
            WHERE ut.fk_usuario_id = %s
              AND t.ativo = 1
              AND m.ativo = 1
        """, (aluno_id,))

        materias = cursor.fetchall()

        if not materias:
            return jsonify({"percentual": 0, "total": 0, "presencas": 0, "faltas": 0})

        total_geral = 0
        presencas_geral = 0
        faltas_geral = 0

        for row in materias:
            cursor.execute("""
                SELECT
                    COUNT(id)                       AS total,
                    COALESCE(SUM(presente = 1), 0)  AS presencas,
                    COALESCE(SUM(presente = 0), 0)  AS faltas
                FROM frequencia
                WHERE fk_usuario_id = %s AND fk_materia_id = %s
            """, (aluno_id, row["materia_id"]))
            freq = cursor.fetchone()
            total_geral     += freq["total"]
            presencas_geral += freq["presencas"]
            faltas_geral    += freq["faltas"]

        # Mesmo cálculo da tela de frequência: começa em 100%, cada falta desconta 2%
        percentual = round(max(0, 100 - (faltas_geral * 2)), 1)

        return jsonify({
            "percentual": percentual,
            "total":      total_geral,
            "presencas":  presencas_geral,
            "faltas":     faltas_geral,
        })

    finally:
        cursor.close()
        conexao.close()


# ========================
# ALERTAS DE FREQUÊNCIA – PROFESSOR (para o dashboard)
# ========================

@frequencia_bp.get("/api/frequencia/professor/alertas")
def api_alertas_professor():
    """
    Retorna alunos com frequência abaixo de 75% nas turmas/matérias
    onde o professor logado leciona.
    """
    from gerador_token import validar_token

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"alertas": []}), 401

    payload = validar_token(auth.split(" ", 1)[1])
    if not payload or str(payload.get("papel", "")).lower() != "professor":
        return jsonify({"alertas": []}), 403

    professor_id = payload.get("id")
    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    try:
        # Matérias + turmas do professor
        cursor.execute("""
            SELECT DISTINCT
                m.id   AS materia_id,
                m.nome AS materia_nome,
                t.id   AS turma_id,
                t.nome AS turma_nome
            FROM professor_materia pm
            INNER JOIN materia m ON m.id = pm.fk_materia_id
            INNER JOIN materias_turma mt ON mt.fk_materia_id = m.id
            INNER JOIN turma t ON t.id = mt.fk_turma_id
            WHERE pm.fk_usuario_id = %s AND m.ativo = 1 AND t.ativo = 1
        """, (professor_id,))

        combos = cursor.fetchall()
        alertas = []

        for combo in combos:
            cursor.execute("""
                SELECT
                    u.id,
                    u.nome,
                    COUNT(f.id)                       AS total,
                    COALESCE(SUM(f.presente = 1), 0)  AS presencas,
                    COALESCE(SUM(f.presente = 0), 0)  AS faltas
                FROM usuario u
                INNER JOIN usuario_turma ut ON ut.fk_usuario_id = u.id
                INNER JOIN papel p ON p.id = u.fk_papel_id
                LEFT JOIN frequencia f
                    ON f.fk_usuario_id = u.id
                   AND f.fk_materia_id = %s
                WHERE ut.fk_turma_id = %s
                  AND LOWER(p.descricao) = 'aluno'
                  AND u.ativo = 1
                GROUP BY u.id, u.nome
            """, (combo["materia_id"], combo["turma_id"]))

            alunos = cursor.fetchall()
            for a in alunos:
                if a["total"] == 0:
                    continue
                # Mesmo cálculo da tela de frequência: 100% - (faltas * 2%)
                pct = round(max(0, 100 - (a["faltas"] * 2)), 1)
                if pct < 75:
                    alertas.append({
                        "nome":      a["nome"],
                        "turma":     combo["turma_nome"],
                        "materia":   combo["materia_nome"],
                        "percentual": pct,
                    })

        # Ordena pelo percentual mais baixo primeiro
        alertas.sort(key=lambda x: x["percentual"])
        return jsonify({"alertas": alertas[:20]})

    finally:
        cursor.close()
        conexao.close()


# ========================
# ALERTAS DE FREQUÊNCIA – COORDENADOR (para o dashboard)
# ========================

@frequencia_bp.get("/api/frequencia/coordenador/alertas")
def api_alertas_coordenador():
    """
    Retorna alunos com frequência abaixo de 75% em qualquer matéria.
    Usado no dashboard do coordenador.
    """
    from gerador_token import validar_token

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"alertas": []}), 401

    payload = validar_token(auth.split(" ", 1)[1])
    papel = str(payload.get("papel", "")).lower() if payload else ""
    if papel not in ("coordenador", "admin", "adm"):
        return jsonify({"alertas": []}), 403

    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    try:
        # Agrupa presença por aluno×matéria em todas as turmas ativas
        cursor.execute("""
            SELECT
                u.id,
                u.nome,
                m.nome AS materia_nome,
                t.nome AS turma_nome,
                COUNT(f.id)                       AS total,
                COALESCE(SUM(f.presente = 1), 0)  AS presencas,
                COALESCE(SUM(f.presente = 0), 0)  AS faltas
            FROM usuario u
            INNER JOIN papel p          ON p.id  = u.fk_papel_id
            INNER JOIN usuario_turma ut ON ut.fk_usuario_id = u.id
            INNER JOIN turma t          ON t.id  = ut.fk_turma_id AND t.ativo = 1
            INNER JOIN materias_turma mt ON mt.fk_turma_id = t.id
            INNER JOIN materia m         ON m.id = mt.fk_materia_id AND m.ativo = 1
            LEFT  JOIN frequencia f
                ON f.fk_usuario_id = u.id
               AND f.fk_materia_id = m.id
            WHERE LOWER(p.descricao) = 'aluno'
              AND u.ativo = 1
            GROUP BY u.id, u.nome, m.id, m.nome, t.id, t.nome
            HAVING total > 0
            ORDER BY presencas / total ASC
            LIMIT 30
        """)

        rows = cursor.fetchall()
        alertas = []
        for r in rows:
            # Mesmo cálculo da tela de frequência: 100% - (faltas * 2%)
            pct = round(max(0, 100 - (r["faltas"] * 2)), 1)
            if pct < 75:
                alertas.append({
                    "mensagem": f"{r['nome']} — {r['materia_nome']} ({r['turma_nome']}): {pct}%",
                    "nome":      r["nome"],
                    "materia":   r["materia_nome"],
                    "turma":     r["turma_nome"],
                    "percentual": pct,
                })

        return jsonify({"alertas": alertas})

    finally:
        cursor.close()
        conexao.close()


# ========================
# RESUMO GERAL DE FREQUÊNCIA – COORDENADOR (para o donut do dashboard)
# ========================

@frequencia_bp.get("/api/frequencia/coordenador/resumo")
def api_resumo_coordenador():
    """
    Retorna a frequência média geral de TODOS os alunos em todas as matérias.
    Usa o mesmo cálculo da tela de frequência: 100% - (faltas * 2%).
    Usado no donut do dashboard do coordenador.
    """
    from gerador_token import validar_token

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Não autorizado"}), 401

    payload = validar_token(auth.split(" ", 1)[1])
    papel = str(payload.get("papel", "")).lower() if payload else ""
    if papel not in ("coordenador", "admin", "adm"):
        return jsonify({"error": "Sem permissão"}), 403

    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    try:
        # Busca todos os pares aluno×matéria com frequência registrada
        cursor.execute("""
            SELECT
                f.fk_usuario_id,
                f.fk_materia_id,
                COALESCE(SUM(f.presente = 0), 0) AS faltas,
                COUNT(f.id)                       AS total
            FROM frequencia f
            INNER JOIN usuario u   ON u.id = f.fk_usuario_id AND u.ativo = 1
            INNER JOIN papel p     ON p.id = u.fk_papel_id AND LOWER(p.descricao) = 'aluno'
            INNER JOIN materia m   ON m.id = f.fk_materia_id AND m.ativo = 1
            GROUP BY f.fk_usuario_id, f.fk_materia_id
            HAVING total > 0
        """)

        pares = cursor.fetchall()

        if not pares:
            return jsonify({
                "percentual": 100.0,
                "total_aulas": 0,
                "total_faltas": 0,
                "total_pares": 0,
            })

        # Média das frequências individuais (igual à fórmula da tela)
        soma_pct = sum(max(0, 100 - (row["faltas"] * 2)) for row in pares)
        percentual = round(soma_pct / len(pares), 1)

        total_aulas  = sum(row["total"]  for row in pares)
        total_faltas = sum(row["faltas"] for row in pares)

        return jsonify({
            "percentual":   percentual,
            "total_aulas":  total_aulas,
            "total_faltas": total_faltas,
            "total_pares":  len(pares),
        })

    finally:
        cursor.close()
        conexao.close()

@frequencia_bp.route("/frequencia/relatorio")
def relatorio_frequencia():
    aluno_id   = request.args.get("aluno")
    materia_id = request.args.get("materia")
    turma_id   = request.args.get("turma")

    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT nome FROM usuario WHERE id = %s", (aluno_id,))
    aluno = cursor.fetchone()

    cursor.execute("SELECT nome, periodo FROM turma WHERE id = %s", (turma_id,))
    turma = cursor.fetchone()

    cursor.execute("SELECT nome FROM materia WHERE id = %s", (materia_id,))
    materia = cursor.fetchone()

    cursor.execute("""
        SELECT
            COUNT(id)                       AS total,
            COALESCE(SUM(presente = 1), 0)  AS presencas,
            COALESCE(SUM(presente = 0), 0)  AS faltas
        FROM frequencia
        WHERE fk_usuario_id = %s AND fk_materia_id = %s
    """, (aluno_id, materia_id))

    freq = cursor.fetchone()

    cursor.close()
    conexao.close()

    total     = freq["total"]
    presencas = freq["presencas"]
    faltas    = freq["faltas"]
    pct_raw   = max(0, 100 - (faltas * 2))
    percentual = f"{pct_raw}%"

    turma_label  = f"{turma['nome']} ({turma['periodo']}º Período)" if turma else "—"
    materia_label = materia["nome"] if materia else "—"

    conteudo = (
        f"RELATÓRIO DE FREQUÊNCIA\n\n"
        f"Aluno:      {aluno['nome']}\n"
        f"Turma:      {turma_label}\n"
        f"Matéria:    {materia_label}\n"
        f"Total:      {total}\n"
        f"Presenças:  {presencas}\n"
        f"Faltas:     {faltas}\n"
        f"Frequência: {percentual}\n"
    )

    return Response(
        conteudo,
        mimetype="text/plain",
        headers={
            "Content-Disposition": "attachment; filename=relatorio_frequencia.txt"
        },
    )