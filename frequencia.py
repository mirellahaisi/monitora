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
# RELATÓRIO
# ========================

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