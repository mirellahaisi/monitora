from flask import Blueprint, render_template, request, make_response
from .conexao import criar_conexao
import io

desempenho_bp = Blueprint("desempenho", __name__)

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