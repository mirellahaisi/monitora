from flask import Blueprint, jsonify, render_template, request
import mysql.connector

from conexao import criar_conexao
from login import token_obrigatorio, papel_obrigatorio

notas_bp = Blueprint("notas", __name__)


@notas_bp.get("/notas")
def tela_notas():
    return render_template("pages/notas.html", active_page='notas')


@notas_bp.get("/api/notas/materias")
@token_obrigatorio
@papel_obrigatorio("professor")
def listar_materias_professor(usuario):
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT m.id, m.nome
            FROM materia m
            INNER JOIN professor_materia pm
                ON pm.fk_materia_id = m.id
            WHERE pm.fk_usuario_id = %s
              AND m.ativo = 1
            ORDER BY m.nome
        """, (usuario["id"],))

        return jsonify({"materias": cursor.fetchall()}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar matérias.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@notas_bp.get("/api/notas/turmas")
@token_obrigatorio
@papel_obrigatorio("professor")
def listar_turmas_por_materia(usuario):
    materia_id = request.args.get("materia_id")

    if not materia_id:
        return jsonify({"message": "Informe a matéria."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT t.id, t.nome, t.periodo
            FROM turma t
            INNER JOIN materias_turma mt
                ON mt.fk_turma_id = t.id
            INNER JOIN professor_materia pm
                ON pm.fk_materia_id = mt.fk_materia_id
            WHERE pm.fk_usuario_id = %s
              AND mt.fk_materia_id = %s
              AND t.ativo = 1
            ORDER BY t.nome
        """, (usuario["id"], materia_id))

        return jsonify({"turmas": cursor.fetchall()}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar turmas.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@notas_bp.get("/api/notas/alunos")
@token_obrigatorio
@papel_obrigatorio("professor")
def listar_alunos_da_turma(usuario):
    materia_id = request.args.get("materia_id")
    turma_id = request.args.get("turma_id")

    if not materia_id or not turma_id:
        return jsonify({"message": "Informe matéria e turma."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                u.id,
                u.nome,
                MAX(CASE WHEN n.observacao = 'nota1' THEN n.valor END) AS nota1,
                MAX(CASE WHEN n.observacao = 'nota2' THEN n.valor END) AS nota2
            FROM usuario u
            INNER JOIN usuario_turma ut
                ON ut.fk_usuario_id = u.id
            INNER JOIN papel p
                ON p.id = u.fk_papel_id
            LEFT JOIN nota n
                ON n.fk_usuario_id = u.id
               AND n.fk_materia_id = %s
            WHERE ut.fk_turma_id = %s
              AND LOWER(p.descricao) = 'aluno'
              AND u.ativo = 1
            GROUP BY u.id, u.nome
            ORDER BY u.nome
        """, (materia_id, turma_id))

        alunos = cursor.fetchall()

        for aluno in alunos:
            nota1 = aluno["nota1"]
            nota2 = aluno["nota2"]

            aluno["nota1"] = float(nota1) if nota1 is not None else None
            aluno["nota2"] = float(nota2) if nota2 is not None else None

            if nota1 is not None and nota2 is not None:
                aluno["media"] = round((float(nota1) + float(nota2)) / 2, 2)
            else:
                aluno["media"] = None

        return jsonify({"alunos": alunos}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar alunos.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@notas_bp.get("/api/notas/minhas-notas")
@token_obrigatorio
def minhas_notas(usuario):
    """
    Aluno → retorna todas as matérias da sua turma com as notas e média de cada uma.
    """
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                m.id         AS materia_id,
                m.nome       AS materia_nome,
                m.carga_horaria,
                GROUP_CONCAT(DISTINCT u.nome ORDER BY u.nome SEPARATOR ', ') AS professores,
                MAX(CASE WHEN n.observacao = 'nota1' THEN n.valor END) AS nota1,
                MAX(CASE WHEN n.observacao = 'nota2' THEN n.valor END) AS nota2
            FROM materia m
            INNER JOIN materias_turma mt ON mt.fk_materia_id = m.id
            INNER JOIN usuario_turma ut  ON ut.fk_turma_id   = mt.fk_turma_id
                                        AND ut.fk_usuario_id = %s
            LEFT JOIN professor_materia pm ON pm.fk_materia_id = m.id
            LEFT JOIN usuario u            ON u.id = pm.fk_usuario_id AND u.ativo = 1
            LEFT JOIN nota n               ON n.fk_usuario_id  = %s
                                          AND n.fk_materia_id  = m.id
            WHERE m.ativo = 1
            GROUP BY m.id, m.nome, m.carga_horaria
            ORDER BY m.nome
        """, (usuario["id"], usuario["id"]))

        materias = cursor.fetchall()

        for mat in materias:
            n1 = mat["nota1"]
            n2 = mat["nota2"]
            mat["nota1"] = float(n1) if n1 is not None else None
            mat["nota2"] = float(n2) if n2 is not None else None
            if n1 is not None and n2 is not None:
                mat["media"] = round((float(n1) + float(n2)) / 2, 2)
            else:
                mat["media"] = None

        return jsonify({"materias": materias}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar suas notas.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()

# ========================
# ROTAS DO COORDENADOR - NOTAS
# ========================

@notas_bp.get("/api/notas/coordenador/materias")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def listar_materias_coordenador(usuario):
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome
            FROM materia
            WHERE ativo = 1
            ORDER BY nome
        """)

        return jsonify({"materias": cursor.fetchall()}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar matérias.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@notas_bp.get("/api/notas/coordenador/turmas")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def listar_turmas_coordenador(usuario):
    materia_id = request.args.get("materia_id")

    if not materia_id:
        return jsonify({"message": "Informe a matéria."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT t.id, t.nome, t.periodo
            FROM turma t
            INNER JOIN materias_turma mt
                ON mt.fk_turma_id = t.id
            WHERE mt.fk_materia_id = %s
              AND t.ativo = 1
            ORDER BY t.periodo, t.nome
        """, (materia_id,))

        return jsonify({"turmas": cursor.fetchall()}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar turmas.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@notas_bp.get("/api/notas/coordenador/professores")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def listar_professores_coordenador(usuario):
    materia_id = request.args.get("materia_id")
    turma_id = request.args.get("turma_id")

    if not materia_id or not turma_id:
        return jsonify({"message": "Informe matéria e turma."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT u.id, u.nome
            FROM usuario u
            INNER JOIN professor_materia pm
                ON pm.fk_usuario_id = u.id
            INNER JOIN materias_turma mt
                ON mt.fk_materia_id = pm.fk_materia_id
            INNER JOIN papel p
                ON p.id = u.fk_papel_id
            WHERE pm.fk_materia_id = %s
              AND mt.fk_turma_id = %s
              AND LOWER(p.descricao) = 'professor'
              AND u.ativo = 1
            ORDER BY u.nome
        """, (materia_id, turma_id))

        return jsonify({"professores": cursor.fetchall()}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar professores.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@notas_bp.get("/api/notas/coordenador/alunos")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def listar_notas_coordenador(usuario):
    materia_id = request.args.get("materia_id")
    turma_id = request.args.get("turma_id")
    professor_id = request.args.get("professor_id")

    if not materia_id or not turma_id:
        return jsonify({"message": "Informe matéria e turma."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        parametros = [materia_id, turma_id, materia_id]
        filtro_professor = ""

        if professor_id:
            filtro_professor = " AND prof.id = %s "
            parametros.append(professor_id)

        cursor.execute(f"""
            SELECT
                aluno.id AS aluno_id,
                aluno.nome AS aluno_nome,
                GROUP_CONCAT(DISTINCT prof.nome ORDER BY prof.nome SEPARATOR ', ') AS professores,
                MAX(CASE WHEN n.observacao = 'nota1' THEN n.valor END) AS nota1,
                MAX(CASE WHEN n.observacao = 'nota2' THEN n.valor END) AS nota2
            FROM usuario aluno
            INNER JOIN usuario_turma ut
                ON ut.fk_usuario_id = aluno.id
            INNER JOIN papel p_aluno
                ON p_aluno.id = aluno.fk_papel_id
            LEFT JOIN nota n
                ON n.fk_usuario_id = aluno.id
               AND n.fk_materia_id = %s
            LEFT JOIN professor_materia pm
                ON pm.fk_materia_id = %s
            LEFT JOIN usuario prof
                ON prof.id = pm.fk_usuario_id
               AND prof.ativo = 1
            WHERE ut.fk_turma_id = %s
              AND LOWER(p_aluno.descricao) = 'aluno'
              AND aluno.ativo = 1
              {filtro_professor}
            GROUP BY aluno.id, aluno.nome
            ORDER BY aluno.nome
        """, tuple(parametros))

        alunos = cursor.fetchall()

        for aluno in alunos:
            nota1 = aluno["nota1"]
            nota2 = aluno["nota2"]

            aluno["id"] = aluno["aluno_id"]
            aluno["nome"] = aluno["aluno_nome"]
            aluno["nota1"] = float(nota1) if nota1 is not None else None
            aluno["nota2"] = float(nota2) if nota2 is not None else None

            if nota1 is not None and nota2 is not None:
                aluno["media"] = round((float(nota1) + float(nota2)) / 2, 2)
            else:
                aluno["media"] = None

        return jsonify({"alunos": alunos}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar notas.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()

@notas_bp.post("/api/notas/salvar")
@token_obrigatorio
@papel_obrigatorio("professor")
def salvar_notas(usuario):
    dados = request.get_json(silent=True) or {}

    materia_id = dados.get("materia_id")
    alunos = dados.get("alunos", [])

    if not materia_id or not alunos:
        return jsonify({"message": "Informe a matéria e as notas."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()

        for aluno in alunos:
            aluno_id = aluno.get("aluno_id")
            nota1 = aluno.get("nota1")
            nota2 = aluno.get("nota2")

            for observacao, valor in [("nota1", nota1), ("nota2", nota2)]:
                if valor in ("", None):
                    continue

                cursor.execute("""
                    SELECT id
                    FROM nota
                    WHERE fk_usuario_id = %s
                      AND fk_materia_id = %s
                      AND observacao = %s
                    LIMIT 1
                """, (aluno_id, materia_id, observacao))

                nota_existente = cursor.fetchone()

                if nota_existente:
                    cursor.execute("""
                        UPDATE nota
                        SET valor = %s,
                            data_lancamento = NOW()
                        WHERE fk_usuario_id = %s
                          AND fk_materia_id = %s
                          AND observacao = %s
                    """, (valor, aluno_id, materia_id, observacao))
                else:
                    cursor.execute("""
                        INSERT INTO nota (
                            valor,
                            observacao,
                            data_lancamento,
                            fk_materia_id,
                            fk_usuario_id
                        ) VALUES (%s, %s, NOW(), %s, %s)
                    """, (valor, observacao, materia_id, aluno_id))

        conexao.commit()

        return jsonify({"message": "Notas salvas com sucesso."}), 200

    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()
        return jsonify({"message": "Erro ao salvar notas.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


# ========================
# ROTAS DO COORDENADOR - FLUXO: PROFESSOR → TURMA → MATÉRIA → NOTAS (papel 1)
# ========================

@notas_bp.get("/api/notas/coordenador/professores-lista")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def listar_todos_professores(usuario):
    """Retorna todos os professores ativos (primeiro select da view do coordenador)."""
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT u.id, u.nome
            FROM usuario u
            INNER JOIN papel p ON p.id = u.fk_papel_id
            WHERE LOWER(p.descricao) = 'professor'
              AND u.ativo = 1
            ORDER BY u.nome
        """)

        return jsonify({"professores": cursor.fetchall()}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar professores.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@notas_bp.get("/api/notas/coordenador/turmas-por-professor")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def listar_turmas_por_professor(usuario):
    """Retorna as turmas em que o professor leciona (segundo select da view do coordenador)."""
    professor_id = request.args.get("professor_id")

    if not professor_id:
        return jsonify({"message": "Informe o professor."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT t.id, t.nome, t.periodo
            FROM turma t
            INNER JOIN materias_turma mt
                ON mt.fk_turma_id = t.id
            INNER JOIN professor_materia pm
                ON pm.fk_materia_id = mt.fk_materia_id
            WHERE pm.fk_usuario_id = %s
              AND t.ativo = 1
            ORDER BY t.periodo, t.nome
        """, (professor_id,))

        return jsonify({"turmas": cursor.fetchall()}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar turmas.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@notas_bp.get("/api/notas/coordenador/materias-por-professor-turma")
@token_obrigatorio
@papel_obrigatorio("coordenador", "admin", "adm")
def listar_materias_professor_turma(usuario):
    """Retorna as matérias que o professor leciona naquela turma (terceiro select da view do coordenador)."""
    professor_id = request.args.get("professor_id")
    turma_id     = request.args.get("turma_id")

    if not professor_id or not turma_id:
        return jsonify({"message": "Informe o professor e a turma."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT m.id, m.nome
            FROM materia m
            INNER JOIN professor_materia pm
                ON pm.fk_materia_id = m.id
            INNER JOIN materias_turma mt
                ON mt.fk_materia_id = m.id
            WHERE pm.fk_usuario_id = %s
              AND mt.fk_turma_id = %s
              AND m.ativo = 1
            ORDER BY m.nome
        """, (professor_id, turma_id))

        return jsonify({"materias": cursor.fetchall()}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar matérias.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()