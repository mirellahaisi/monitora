from flask import Blueprint, render_template, request, Response, jsonify

from conexao import criar_conexao

frequencia_bp = Blueprint("frequencia", __name__)


# ========================
# ROTAS DE TELA
# ========================

@frequencia_bp.route("/frequencia")
def frequencia():
    aluno_id   = request.args.get("aluno")
    materia_id = request.args.get("materia")
    turma_id   = request.args.get("turma")

    conexao = criar_conexao()
    cursor  = conexao.cursor(dictionary=True)

    # Lista todos os alunos para o primeiro select
    cursor.execute("""
        SELECT u.id, u.nome
        FROM usuario u
        INNER JOIN papel p ON p.id = u.fk_papel_id
        WHERE LOWER(p.descricao) = 'aluno' AND u.ativo = 1
        ORDER BY u.nome
    """)
    alunos = cursor.fetchall()

    aluno   = None
    mostrar = False
    materia_nome = None
    turma_nome   = None

    if aluno_id and turma_id and materia_id:
        # Busca nome da turma e período
        cursor.execute("""
            SELECT nome, periodo FROM turma WHERE id = %s
        """, (turma_id,))
        turma_row = cursor.fetchone()
        if turma_row:
            turma_nome = f"{turma_row['nome']} (Período {turma_row['periodo']})"

        # Busca nome da matéria
        cursor.execute("SELECT nome FROM materia WHERE id = %s", (materia_id,))
        materia_row = cursor.fetchone()
        if materia_row:
            materia_nome = materia_row["nome"]

        # Frequência filtrada por aluno E matéria
        cursor.execute("""
            SELECT
                u.nome,
                COUNT(f.id)                       AS total,
                COALESCE(SUM(f.presente = 1), 0)  AS presencas,
                COALESCE(SUM(f.presente = 0), 0)  AS faltas
            FROM usuario u
            LEFT JOIN frequencia f
                   ON f.fk_usuario_id = u.id
                  AND f.fk_materia_id = %s
            WHERE u.id = %s
            GROUP BY u.nome
        """, (materia_id, aluno_id))

        result = cursor.fetchone()

        if result:
            total     = result["total"]
            presencas = result["presencas"]
            faltas    = result["faltas"]
            pct_raw   = round((presencas / total) * 100) if total else 0

            aluno = {
                "nome":         result["nome"],
                "total":        total,
                "presencas":    presencas,
                "faltas":       faltas,
                "presenca":     f"{pct_raw}%",
                "presenca_raw": pct_raw,
            }
            mostrar = True

    cursor.close()
    conexao.close()

    return render_template(
        "pages/frequencia.html",
        alunos=alunos,
        mostrar=mostrar,
        aluno=aluno,
        materia=materia_nome,
        periodo=turma_nome,
        active_page="frequencia",
    )


# ========================
# APIS PARA OS SELECTS DINÂMICOS
# ========================

@frequencia_bp.get("/api/frequencia/turmas")
def api_turmas_por_aluno():
    """Retorna as turmas do aluno selecionado."""
    aluno_id = request.args.get("aluno_id")

    if not aluno_id:
        return jsonify([])

    conexao = criar_conexao()
    cursor  = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT t.id, t.nome, t.periodo
        FROM turma t
        INNER JOIN usuario_turma ut ON ut.fk_turma_id = t.id
        WHERE ut.fk_usuario_id = %s AND t.ativo = 1
        ORDER BY t.periodo
    """, (aluno_id,))

    turmas = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(turmas)


@frequencia_bp.get("/api/frequencia/materias")
def api_materias_por_turma():
    """Retorna as matérias da turma selecionada."""
    turma_id = request.args.get("turma_id")

    if not turma_id:
        return jsonify([])

    conexao = criar_conexao()
    cursor  = conexao.cursor(dictionary=True)

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


# ========================
# RELATÓRIO
# ========================

@frequencia_bp.route("/frequencia/relatorio")
def relatorio_frequencia():
    aluno_id   = request.args.get("aluno")
    materia_id = request.args.get("materia")
    turma_id   = request.args.get("turma")

    conexao = criar_conexao()
    cursor  = conexao.cursor(dictionary=True)

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

    total      = freq["total"]
    presencas  = freq["presencas"]
    faltas     = freq["faltas"]
    percentual = f"{round((presencas / total) * 100)}%" if total else "0%"

    turma_label   = f"{turma['nome']} (Período {turma['periodo']})" if turma else "—"
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
        headers={"Content-Disposition": "attachment; filename=relatorio_frequencia.txt"},
    )