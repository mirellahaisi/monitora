from flask import Blueprint, render_template, request, jsonify
from .conexao import criar_conexao
from .login import token_obrigatorio, papel_obrigatorio

desempenho_bp = Blueprint("desempenho", __name__)

PAPEIS_PERMITIDOS = ("professor", "coordenador", "admin", "adm")

@desempenho_bp.route("/desempenho")
def desempenho():
    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    # Lista todos os alunos
    cursor.execute("""
        SELECT u.id, u.nome
        FROM usuario u
        INNER JOIN papel p ON p.id = u.fk_papel_id
        WHERE LOWER(p.descricao) = 'aluno' AND u.ativo = 1
        ORDER BY u.nome
    """)
    alunos = cursor.fetchall()

    aluno_id = request.args.get("aluno")
    dados = None

    if aluno_id:
        # Dados do aluno e turma
        cursor.execute("""
            SELECT u.nome, u.cpf AS matricula, t.periodo
            FROM usuario u
            LEFT JOIN usuario_turma ut ON ut.fk_usuario_id = u.id
            LEFT JOIN turma t ON t.id = ut.fk_turma_id
            WHERE u.id = %s
            LIMIT 1
        """, (aluno_id,))
        aluno = cursor.fetchone()

        # Frequência
        cursor.execute("""
            SELECT
                COUNT(id) AS total,
                COALESCE(SUM(presente = 1), 0) AS presencas,
                COALESCE(SUM(presente = 0), 0) AS faltas
            FROM frequencia
            WHERE fk_usuario_id = %s
        """, (aluno_id,))
        freq = cursor.fetchone()

        total = freq["total"] or 0
        presencas = freq["presencas"] or 0
        faltas = freq["faltas"] or 0
        pct_frequencia = round((presencas / total) * 100) if total else 0

        # Notas por matéria (para o gráfico)
        cursor.execute("""
            SELECT m.nome AS materia, AVG(n.valor) AS media
            FROM nota n
            INNER JOIN materia m ON m.id = n.fk_materia_id
            WHERE n.fk_usuario_id = %s
            GROUP BY m.nome
            ORDER BY m.nome
        """, (aluno_id,))
        notas_por_materia = cursor.fetchall()

        # Média geral
        cursor.execute("""
            SELECT AVG(valor) AS media_geral
            FROM nota
            WHERE fk_usuario_id = %s
        """, (aluno_id,))
        media_row = cursor.fetchone()
        media_geral = round(float(media_row["media_geral"]), 1) if media_row["media_geral"] else 0

        # Participação (baseada em presenças)
        participacao = min(100, round(pct_frequencia * 1.08)) if pct_frequencia else 0

        dados = {
            "nome": aluno["nome"] if aluno else "—",
            "matricula": aluno.get("matricula", "—") if aluno else "—",
            "periodo": f"{aluno['periodo']} período" if aluno and aluno["periodo"] else "—",
            "total_aulas": total,
            "presencas": presencas,
            "faltas": faltas,
            "pct_frequencia": pct_frequencia,
            "pct_faltas": 100 - pct_frequencia,
            "media_geral": media_geral,
            "participacao": participacao,
            "notas_por_materia": notas_por_materia,
        }

    cursor.close()
    conexao.close()

    return render_template(
        "pages/desempenho.html",
        alunos=alunos,
        dados=dados,
        aluno_id=aluno_id,
        active_page="desempenho"
    )


@desempenho_bp.route("/api/desempenho/turmas")
@token_obrigatorio
@papel_obrigatorio(*PAPEIS_PERMITIDOS)
def api_desempenho_turmas(usuario):
    papel = str(usuario.get("papel", "")).lower()
    usuario_id = usuario.get("id")

    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    if papel == "professor":
        # Apenas turmas em que o professor dá aulas
        cursor.execute("""
            SELECT DISTINCT t.id, t.nome, t.periodo, c.nome AS curso_nome
            FROM turma t
            INNER JOIN curso c ON c.id = t.fk_curso_id
            INNER JOIN professor_turma_materia ptm ON ptm.fk_turma_id = t.id
            WHERE ptm.fk_usuario_id = %s AND t.ativo = 1
            ORDER BY c.nome, t.periodo, t.nome
        """, (usuario_id,))
    else:
        cursor.execute("""
            SELECT t.id, t.nome, t.periodo, c.nome AS curso_nome
            FROM turma t
            INNER JOIN curso c ON c.id = t.fk_curso_id
            WHERE t.ativo = 1
            ORDER BY c.nome, t.periodo, t.nome
        """)
    turmas = cursor.fetchall()
    cursor.close()
    conexao.close()
    return jsonify(turmas)


@desempenho_bp.route("/api/desempenho/materias")
@token_obrigatorio
@papel_obrigatorio(*PAPEIS_PERMITIDOS)
def api_desempenho_materias(usuario):
    turma_id = request.args.get("turma_id")
    if not turma_id:
        return jsonify([])

    papel = str(usuario.get("papel", "")).lower()
    usuario_id = usuario.get("id")

    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    if papel == "professor":
        # Apenas matérias que o professor leciona nessa turma
        cursor.execute("""
            SELECT DISTINCT m.id, m.nome
            FROM materia m
            INNER JOIN professor_turma_materia ptm ON ptm.fk_materia_id = m.id
            WHERE ptm.fk_turma_id = %s AND ptm.fk_usuario_id = %s AND m.ativo = 1
            ORDER BY m.nome
        """, (turma_id, usuario_id))
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


@desempenho_bp.route("/api/desempenho/relatorio-turma")
@token_obrigatorio
@papel_obrigatorio(*PAPEIS_PERMITIDOS)
def api_relatorio_turma(usuario):
    turma_id  = request.args.get("turma_id")
    materia_id = request.args.get("materia_id")
    if not turma_id or not materia_id:
        return jsonify({"erro": "turma_id e materia_id são obrigatórios"}), 400

    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    # Dados da turma e curso
    cursor.execute("""
        SELECT t.nome AS turma_nome, t.periodo, c.nome AS curso_nome
        FROM turma t
        INNER JOIN curso c ON c.id = t.fk_curso_id
        WHERE t.id = %s
    """, (turma_id,))
    turma = cursor.fetchone()

    # Nome da matéria
    cursor.execute("SELECT nome FROM materia WHERE id = %s", (materia_id,))
    materia = cursor.fetchone()

    # Professor responsável pela matéria nessa turma
    cursor.execute("""
        SELECT u.nome
        FROM professor_turma_materia ptm
        INNER JOIN usuario u ON u.id = ptm.fk_usuario_id
        WHERE ptm.fk_turma_id = %s AND ptm.fk_materia_id = %s
        LIMIT 1
    """, (turma_id, materia_id))
    prof_row = cursor.fetchone()
    professor = prof_row["nome"] if prof_row else "—"

    # Notas dos alunos da turma nessa matéria
    cursor.execute("""
        SELECT
            u.id,
            u.nome,
            MAX(CASE WHEN LOWER(n.observacao) LIKE '%1%' THEN n.valor END) AS nota1,
            MAX(CASE WHEN LOWER(n.observacao) LIKE '%2%' THEN n.valor END) AS nota2,
            AVG(n.valor) AS media
        FROM usuario u
        INNER JOIN usuario_turma ut ON ut.fk_usuario_id = u.id
        INNER JOIN papel p ON p.id = u.fk_papel_id
        LEFT JOIN nota n ON n.fk_usuario_id = u.id AND n.fk_materia_id = %s
        WHERE ut.fk_turma_id = %s
          AND u.ativo = 1
          AND LOWER(p.descricao) = 'aluno'
        GROUP BY u.id, u.nome
        ORDER BY u.nome
    """, (materia_id, turma_id))
    alunos_raw = cursor.fetchall()

    cursor.close()
    conexao.close()

    APROVACAO = 7.0
    alunos = []
    soma = 0
    aprovados = 0
    reprovados = 0
    dist = {"0_5": 0, "6_7": 0, "8_10": 0}

    for a in alunos_raw:
        n1    = float(a["nota1"]) if a["nota1"] is not None else None
        n2    = float(a["nota2"]) if a["nota2"] is not None else None
        media = float(a["media"]) if a["media"] is not None else None

        if media is not None:
            soma += media
            if media >= APROVACAO:
                aprovados += 1
            else:
                reprovados += 1
            if media < 6:
                dist["0_5"] += 1
            elif media < 8:
                dist["6_7"] += 1
            else:
                dist["8_10"] += 1

        alunos.append({
            "nome":  a["nome"],
            "nota1": round(n1, 1) if n1 is not None else None,
            "nota2": round(n2, 1) if n2 is not None else None,
            "media": round(media, 2) if media is not None else None,
            "aprovado": media is not None and media >= APROVACAO,
        })

    total_com_nota = aprovados + reprovados
    media_geral = round(soma / total_com_nota, 2) if total_com_nota else 0

    return jsonify({
        "turma_nome":  turma["turma_nome"] if turma else "—",
        "curso_nome":  turma["curso_nome"] if turma else "—",
        "periodo":     f"{turma['periodo']}º período" if turma else "—",
        "materia_nome": materia["nome"] if materia else "—",
        "professor":   professor,
        "media_geral": media_geral,
        "aprovados":   aprovados,
        "reprovados":  reprovados,
        "total":       len(alunos),
        "distribuicao": dist,
        "alunos":      alunos,
    })