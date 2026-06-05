from flask import Blueprint, jsonify, render_template, request
import mysql.connector

from conexao import criar_conexao
from login import token_obrigatorio, papel_obrigatorio

turmas_bp = Blueprint("turmas", __name__)


def _normalizar_turno(turno):
    return str(turno or "").strip()


def _sigla_turno(turno):
    turno_normalizado = _normalizar_turno(turno)
    return turno_normalizado[0].upper() if turno_normalizado else ""


def _normalizar_letra_turma(letra):
    letra_normalizada = str(letra or "").strip().upper()
    if len(letra_normalizada) == 1 and letra_normalizada.isalpha():
        return letra_normalizada
    return None


def _extrair_letra_do_codigo(codigo, prefixo, ano, semestre, turno_sigla):
    codigo_normalizado = str(codigo or "").strip().upper()
    prefixo_normalizado = str(prefixo or "").strip().upper()
    base_codigo = f"{prefixo_normalizado}-{ano}-{semestre}-{turno_sigla}"

    if (
        codigo_normalizado.startswith(base_codigo)
        and len(codigo_normalizado) == len(base_codigo) + 1
    ):
        return _normalizar_letra_turma(codigo_normalizado[-1])

    return None


def _montar_nome_turma(prefixo, ano, semestre, turno, letra):
    sufixo_turma = f" {letra}" if letra != "A" else ""
    return f"{prefixo} {ano}.{semestre} - {turno}{sufixo_turma}"


def _buscar_proxima_letra_turma(
    cursor,
    *,
    curso_id,
    prefixo,
    periodo,
    ano,
    semestre,
    turno,
    turma_id_ignorar=None,
    letra_preferida=None,
):
    turno_normalizado = _normalizar_turno(turno)
    turno_sigla = _sigla_turno(turno_normalizado)
    prefixo_normalizado = str(prefixo or "").strip().upper()

    if not turno_sigla or not prefixo_normalizado:
        return None, None

    parametros_mesma_combinacao = [curso_id, periodo, ano, semestre, turno_normalizado]
    sql_mesma_combinacao = """
        SELECT codigo, turma_letra
        FROM turma
        WHERE fk_curso_id = %s
          AND periodo = %s
          AND ano = %s
          AND semestre = %s
          AND LOWER(TRIM(turno)) = LOWER(TRIM(%s))
    """
    if turma_id_ignorar is not None:
        sql_mesma_combinacao += " AND id != %s"
        parametros_mesma_combinacao.append(turma_id_ignorar)

    cursor.execute(sql_mesma_combinacao, tuple(parametros_mesma_combinacao))
    letras_usadas = set()
    for row in cursor.fetchall():
        letra = _normalizar_letra_turma(row.get("turma_letra"))
        if not letra:
            letra = _extrair_letra_do_codigo(
                row.get("codigo"),
                prefixo_normalizado,
                ano,
                semestre,
                turno_sigla,
            )
        if letra:
            letras_usadas.add(letra)

    padrao_codigo = f"{prefixo_normalizado}-{ano}-{semestre}-{turno_sigla}%"
    parametros_codigos = [padrao_codigo]
    sql_codigos = "SELECT codigo FROM turma WHERE UPPER(TRIM(codigo)) LIKE %s"
    if turma_id_ignorar is not None:
        sql_codigos += " AND id != %s"
        parametros_codigos.append(turma_id_ignorar)

    cursor.execute(sql_codigos, tuple(parametros_codigos))
    codigos_existentes = {
        str(row["codigo"]).strip().upper()
        for row in cursor.fetchall()
        if row.get("codigo")
    }

    ordem_letras = []
    letra_preferida_normalizada = _normalizar_letra_turma(letra_preferida)
    if letra_preferida_normalizada:
        ordem_letras.append(letra_preferida_normalizada)

    ordem_letras.extend(
        chr(ord("A") + indice)
        for indice in range(26)
        if chr(ord("A") + indice) != letra_preferida_normalizada
    )

    for letra in ordem_letras:
        codigo_candidato = f"{prefixo_normalizado}-{ano}-{semestre}-{turno_sigla}{letra}"
        if letra in letras_usadas:
            continue
        if codigo_candidato in codigos_existentes:
            continue
        return letra, codigo_candidato

    return None, None


def _sincronizar_professor_materia_legado(conexao, professor_id, materia_id):
    cursor = None

    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT 1
            FROM professor_turma_materia
            WHERE fk_usuario_id = %s
              AND fk_materia_id = %s
            LIMIT 1
        """, (professor_id, materia_id))

        if cursor.fetchone():
            cursor.execute("""
                INSERT IGNORE INTO professor_materia (fk_usuario_id, fk_materia_id)
                VALUES (%s, %s)
            """, (professor_id, materia_id))
        else:
            cursor.execute("""
                DELETE FROM professor_materia
                WHERE fk_usuario_id = %s
                  AND fk_materia_id = %s
            """, (professor_id, materia_id))
    finally:
        if cursor:
            cursor.close()


# ========================
# ROTA DE TELA
# ========================

@turmas_bp.get("/turmas")
def tela_turmas():
    return render_template("pages/turmas.html", active_page="turmas")


# ========================
# APIS
# ========================

@turmas_bp.get("/api/turmas")
@token_obrigatorio
def listar_turmas(usuario):
    """
    Professor  → apenas as turmas em que leciona.
    Coordenador/Admin → todas as turmas ativas.
    """
    papel = str(usuario.get("papel", "")).lower()
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        if papel == "professor":
            cursor.execute("""
                SELECT
                    t.id,
                    t.nome,
                    t.codigo,
                    t.periodo,
                    t.turno,
                    t.ano,
                    t.semestre,
                    t.capacidade,
                    COUNT(DISTINCT ut.fk_usuario_id) AS total_alunos,
                    GROUP_CONCAT(DISTINCT m.nome ORDER BY m.nome SEPARATOR ', ') AS materias,
                    ROUND(AVG(n.valor), 2) AS media_geral
                FROM turma t
                INNER JOIN professor_turma_materia ptm ON ptm.fk_turma_id = t.id
                INNER JOIN materias_turma mt
                    ON mt.fk_turma_id = t.id
                   AND mt.fk_materia_id = ptm.fk_materia_id
                LEFT JOIN usuario_turma ut ON ut.fk_turma_id = t.id
                LEFT JOIN materia m ON m.id = mt.fk_materia_id AND m.ativo = 1
                LEFT JOIN nota n ON n.fk_usuario_id = ut.fk_usuario_id
                WHERE ptm.fk_usuario_id = %s AND t.ativo = 1
                GROUP BY t.id, t.nome, t.codigo, t.periodo, t.turno, t.ano, t.semestre, t.capacidade
                ORDER BY t.periodo, t.nome
            """, (usuario["id"],))
        else:
            cursor.execute("""
                SELECT
                    t.id,
                    t.nome,
                    t.codigo,
                    t.periodo,
                    t.turno,
                    t.ano,
                    t.semestre,
                    t.capacidade,
                    COUNT(DISTINCT ut.fk_usuario_id) AS total_alunos,
                    GROUP_CONCAT(DISTINCT m.nome ORDER BY m.nome SEPARATOR ', ') AS materias,
                    ROUND(AVG(n.valor), 2) AS media_geral
                FROM turma t
                LEFT JOIN materias_turma mt ON mt.fk_turma_id = t.id
                LEFT JOIN usuario_turma ut ON ut.fk_turma_id = t.id
                LEFT JOIN materia m ON m.id = mt.fk_materia_id AND m.ativo = 1
                LEFT JOIN nota n ON n.fk_usuario_id = ut.fk_usuario_id
                WHERE t.ativo = 1
                GROUP BY t.id, t.nome, t.codigo, t.periodo, t.turno, t.ano, t.semestre, t.capacidade
                ORDER BY t.periodo, t.nome
            """)

        turmas = cursor.fetchall()
        for t in turmas:
            if t.get("media_geral") is not None:
                t["media_geral"] = float(t["media_geral"])
        return jsonify({"turmas": turmas}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar turmas.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.get("/api/minha-turma")
@token_obrigatorio
def minha_turma(usuario):
    """
    Aluno → retorna sua turma e a lista de colegas em ordem alfabética.
    """
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        # Busca a turma do aluno logado
        cursor.execute("""
            SELECT
                t.id,
                t.nome,
                t.codigo,
                t.periodo,
                t.turno,
                t.ano,
                t.semestre,
                t.capacidade,
                COUNT(DISTINCT ut2.fk_usuario_id) AS total_alunos,
                GROUP_CONCAT(DISTINCT m.nome ORDER BY m.nome SEPARATOR ', ') AS materias
            FROM turma t
            INNER JOIN usuario_turma ut ON ut.fk_turma_id = t.id AND ut.fk_usuario_id = %s
            LEFT JOIN usuario_turma ut2 ON ut2.fk_turma_id = t.id
            LEFT JOIN materias_turma mt ON mt.fk_turma_id = t.id
            LEFT JOIN materia m ON m.id = mt.fk_materia_id AND m.ativo = 1
            WHERE t.ativo = 1
            GROUP BY t.id, t.nome, t.codigo, t.periodo, t.turno, t.ano, t.semestre, t.capacidade
            LIMIT 1
        """, (usuario["id"],))

        turma = cursor.fetchone()
        if not turma:
            return jsonify({"message": "Você não está matriculado em nenhuma turma ativa."}), 404

        # Busca os colegas da turma em ordem alfabética
        cursor.execute("""
            SELECT
                u.id,
                u.nome,
                u.email
            FROM usuario u
            INNER JOIN usuario_turma ut ON ut.fk_usuario_id = u.id
            INNER JOIN papel p ON p.id = u.fk_papel_id
            WHERE ut.fk_turma_id = %s
              AND LOWER(p.descricao) = 'aluno'
              AND u.ativo = 1
            ORDER BY u.nome ASC
        """, (turma["id"],))

        alunos = cursor.fetchall()
        return jsonify({"turma": turma, "alunos": alunos}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar sua turma.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.get("/api/turmas/<int:turma_id>/alunos")
@token_obrigatorio
def listar_alunos_turma(usuario, turma_id):
    """Retorna alunos matriculados numa turma com médias gerais."""
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                u.id,
                u.nome,
                u.email,
                ROUND(AVG(n.valor), 2) AS media_geral,
                COUNT(DISTINCT n.fk_materia_id) AS materias_com_nota
            FROM usuario u
            INNER JOIN usuario_turma ut ON ut.fk_usuario_id = u.id
            INNER JOIN papel p ON p.id = u.fk_papel_id
            LEFT JOIN nota n ON n.fk_usuario_id = u.id
            WHERE ut.fk_turma_id = %s
              AND LOWER(p.descricao) = 'aluno'
              AND u.ativo = 1
            GROUP BY u.id, u.nome, u.email
            ORDER BY u.nome
        """, (turma_id,))

        alunos = cursor.fetchall()

        for a in alunos:
            if a["media_geral"] is not None:
                a["media_geral"] = float(a["media_geral"])

        return jsonify({"alunos": alunos}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar alunos.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.get("/api/turmas/<int:turma_id>/materias")
@token_obrigatorio
def listar_materias_turma(usuario, turma_id):
    """Retorna matérias de uma turma com professores atribuídos àquela turma."""
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                m.id,
                m.nome,
                m.carga_horaria,
                u.id AS professor_id,
                u.nome AS professor_nome
            FROM materia m
            INNER JOIN materias_turma mt ON mt.fk_materia_id = m.id
            LEFT JOIN professor_turma_materia ptm
                ON ptm.fk_turma_id = mt.fk_turma_id
               AND ptm.fk_materia_id = m.id
            LEFT JOIN usuario u
                ON u.id = ptm.fk_usuario_id
               AND u.ativo = 1
            WHERE mt.fk_turma_id = %s AND m.ativo = 1
            ORDER BY m.nome, u.nome
        """, (turma_id,))

        materias_map = {}
        for row in cursor.fetchall():
            materia_id = row["id"]

            if materia_id not in materias_map:
                materias_map[materia_id] = {
                    "id": materia_id,
                    "nome": row["nome"],
                    "carga_horaria": row["carga_horaria"],
                    "_professores": [],
                }

            professor_id = row.get("professor_id")
            professor_nome = row.get("professor_nome")
            if professor_id and professor_nome:
                materias_map[materia_id]["_professores"].append({
                    "id": professor_id,
                    "nome": professor_nome,
                })

        materias = []
        for materia in materias_map.values():
            professores = materia.pop("_professores")
            materia["professores"] = ", ".join(prof["nome"] for prof in professores) or None
            materia["professor_ids"] = ",".join(str(prof["id"]) for prof in professores) or None
            materias.append(materia)

        return jsonify({"materias": materias}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar matérias.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.get("/api/turmas/cursos")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador", "professor")
def listar_cursos(usuario):
    """Retorna todos os cursos ativos para popular o select do modal."""
    papel = str(usuario.get("papel", "")).lower()
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        if papel == "professor":
            cursor.execute("""
                SELECT DISTINCT c.id, c.nome, c.codigo_prefixo
                FROM curso c
                INNER JOIN turma t
                    ON t.fk_curso_id = c.id
                INNER JOIN professor_turma_materia ptm
                    ON ptm.fk_turma_id = t.id
                WHERE c.ativo = 1
                  AND t.ativo = 1
                  AND ptm.fk_usuario_id = %s
                ORDER BY c.nome ASC
            """, (usuario["id"],))
        else:
            cursor.execute("""
                SELECT id, nome, codigo_prefixo
                FROM curso
                WHERE ativo = 1
                ORDER BY nome ASC
            """)

        cursos = cursor.fetchall()
        return jsonify({"cursos": cursos}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar cursos.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.post("/api/turmas")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def criar_turma(usuario):
    dados = request.get_json(silent=True) or {}

    # ── Validação dos campos obrigatórios ────────────────────────────────────
    erros = []

    curso_id   = dados.get("curso_id")
    periodo    = dados.get("periodo")
    ano        = dados.get("ano")
    semestre   = dados.get("semestre")
    turno      = dados.get("turno")
    capacidade = dados.get("capacidade")

    if not curso_id:
        erros.append("Selecione um curso.")
    if not periodo:
        erros.append("Campo 'período' é obrigatório.")
    elif not str(periodo).isdigit() or not (1 <= int(periodo) <= 12):
        erros.append("Período deve ser um número entre 1 e 12.")
    # Ano é sempre o corrente, ignoramos o que vier do front
    import datetime
    ano = datetime.date.today().year
    if semestre not in (1, 2, "1", "2"):
        erros.append("Semestre deve ser 1 ou 2.")
    if not turno:
        erros.append("Campo 'turno' é obrigatório.")
    if not capacidade:
        erros.append("Campo 'capacidade' é obrigatório.")
    elif not str(capacidade).isdigit() or not (1 <= int(capacidade) <= 100):
        erros.append("Capacidade deve ser entre 1 e 100.")

    if erros:
        return jsonify({"message": " ".join(erros)}), 400

    curso_id   = int(curso_id)
    periodo    = int(periodo)
    ano        = int(ano)
    semestre   = int(semestre)
    capacidade = int(capacidade)
    turno      = _normalizar_turno(turno)

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        # ── Busca o curso para montar nome e código ──────────────────────────
        cursor.execute(
            "SELECT nome, codigo_prefixo FROM curso WHERE id = %s AND ativo = 1",
            (curso_id,)
        )
        curso = cursor.fetchone()
        if not curso:
            return jsonify({"message": "Curso não encontrado."}), 404

        prefixo = str(curso["codigo_prefixo"] or "").strip().upper()
        nome_curso   = curso["nome"]             # ex: "Análise e Desenvolvimento de Sistemas"
        turno_sigla  = turno[0].upper()          # M / T / N

        # ── Descobre a próxima letra disponível para o código ────────────────
        # Considera TODAS as turmas (ativas e inativas) para evitar conflito
        # de UNIQUE no campo `codigo`, já que turmas desativadas permanecem no banco.
        cursor.execute("""
            SELECT turma_letra
            FROM turma
            WHERE fk_curso_id = %s
              AND ano          = %s
              AND semestre     = %s
              AND LOWER(turno) = LOWER(%s)
        """, (curso_id, ano, semestre, turno))

        letras_usadas = {row["turma_letra"] for row in cursor.fetchall() if row["turma_letra"]}

        # Busca todos os códigos existentes para esse prefixo+ano+semestre+turno
        # em uma única query, evitando múltiplos execute no mesmo cursor
        padrao = f"{prefixo}-{ano}-{semestre}-{turno_sigla}%"
        cursor.execute("SELECT codigo FROM turma WHERE codigo LIKE %s", (padrao,))
        codigos_existentes = {row["codigo"] for row in cursor.fetchall()}

        letra, codigo = _buscar_proxima_letra_turma(
            cursor,
            curso_id=curso_id,
            prefixo=prefixo,
            periodo=periodo,
            ano=ano,
            semestre=semestre,
            turno=turno,
        )

        sufixo_turma = f" {letra}" if letra and letra != "A" else ""

        if not letra:
            return jsonify({"message": "Limite de turmas atingido para esta combinação."}), 409

        nome = f"{prefixo} {ano}.{semestre} — {turno}{sufixo_turma}"

        nome = _montar_nome_turma(prefixo, ano, semestre, turno, letra)

        cursor.execute("""
            INSERT INTO turma
                (fk_curso_id, nome, codigo, periodo, turma_letra, ano, semestre, turno, capacidade, ativo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
        """, (curso_id, nome, codigo, periodo, letra, ano, semestre, turno, capacidade))

        conexao.commit()
        novo_id = cursor.lastrowid
        return jsonify({
            "message": "Turma criada com sucesso.",
            "id":      novo_id,
            "nome":    nome,
            "codigo":  codigo,
        }), 201

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao criar turma.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.get("/api/usuarios/disponiveis")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def listar_usuarios_disponiveis(usuario):
    """Retorna alunos e professores ativos para uso nos selects de gestão."""
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                u.id,
                u.nome,
                u.email,
                LOWER(p.descricao) AS papel,
                CASE
                    WHEN LOWER(p.descricao) = 'aluno'
                         AND EXISTS (
                             SELECT 1 FROM usuario_turma ut
                             INNER JOIN turma t ON t.id = ut.fk_turma_id AND t.ativo = 1
                             WHERE ut.fk_usuario_id = u.id
                         )
                    THEN 1 ELSE 0
                END AS tem_turma
            FROM usuario u
            INNER JOIN papel p ON p.id = u.fk_papel_id
            WHERE u.ativo = 1
              AND LOWER(p.descricao) IN ('aluno', 'professor')
            ORDER BY p.descricao DESC, u.nome ASC
        """)

        usuarios = cursor.fetchall()
        return jsonify({"usuarios": usuarios}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar usuários.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.get("/api/materias/todas")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def listar_todas_materias(usuario):
    """Retorna todas as matérias ativas."""
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome, codigo, carga_horaria
            FROM materia
            WHERE ativo = 1
            ORDER BY nome ASC
        """)

        materias = cursor.fetchall()
        return jsonify({"materias": materias}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao buscar matérias.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.post("/api/turmas/<int:turma_id>/alunos")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def matricular_aluno(usuario, turma_id):
    """Matricula um aluno numa turma (usuario_turma)."""
    dados = request.get_json(silent=True) or {}
    aluno_id = dados.get("usuario_id")
    if not aluno_id:
        return jsonify({"message": "Campo 'usuario_id' é obrigatório."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        # Verifica se o aluno já está matriculado em QUALQUER turma ativa
        cursor.execute("""
            SELECT t.nome AS turma_nome
            FROM usuario_turma ut
            INNER JOIN turma t ON t.id = ut.fk_turma_id AND t.ativo = 1
            WHERE ut.fk_usuario_id = %s
            LIMIT 1
        """, (aluno_id,))
        turma_existente = cursor.fetchone()
        if turma_existente:
            return jsonify({
                "message": f"Este aluno já está matriculado na turma \"{turma_existente['turma_nome']}\". "
                           "Remova-o da turma atual antes de matriculá-lo em outra."
            }), 409

        cursor2 = conexao.cursor()
        cursor2.execute("""
            INSERT INTO usuario_turma (fk_usuario_id, fk_turma_id)
            VALUES (%s, %s)
        """, (aluno_id, turma_id))

        conexao.commit()
        return jsonify({"message": "Aluno matriculado com sucesso."}), 201

    except mysql.connector.Error as erro:
        if "Duplicate entry" in str(erro):
            return jsonify({"message": "Aluno já matriculado nesta turma."}), 409
        return jsonify({"message": "Erro ao matricular aluno.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.delete("/api/turmas/<int:turma_id>/alunos/<int:aluno_id>")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def remover_aluno(usuario, turma_id, aluno_id):
    """Remove um aluno de uma turma."""
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()

        cursor.execute("""
            DELETE FROM usuario_turma
            WHERE fk_usuario_id = %s AND fk_turma_id = %s
        """, (aluno_id, turma_id))

        conexao.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Vínculo não encontrado."}), 404

        return jsonify({"message": "Aluno removido da turma."}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao remover aluno.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.post("/api/turmas/<int:turma_id>/materias")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def vincular_materia(usuario, turma_id):
    """Vincula uma matéria a uma turma (materias_turma)."""
    dados = request.get_json(silent=True) or {}
    materia_id = dados.get("materia_id")
    if not materia_id:
        return jsonify({"message": "Campo 'materia_id' é obrigatório."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO materias_turma (fk_materia_id, fk_turma_id)
            VALUES (%s, %s)
        """, (materia_id, turma_id))

        conexao.commit()
        return jsonify({"message": "Matéria vinculada com sucesso."}), 201

    except mysql.connector.Error as erro:
        if "Duplicate entry" in str(erro):
            return jsonify({"message": "Matéria já vinculada a esta turma."}), 409
        return jsonify({"message": "Erro ao vincular matéria.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.delete("/api/turmas/<int:turma_id>/materias/<int:materia_id>")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def desvincular_materia(usuario, turma_id, materia_id):
    """Remove o vínculo de uma matéria com a turma."""
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()

        cursor.execute("""
            DELETE FROM materias_turma
            WHERE fk_materia_id = %s AND fk_turma_id = %s
        """, (materia_id, turma_id))

        conexao.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Vínculo não encontrado."}), 404

        return jsonify({"message": "Matéria removida da turma."}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao remover matéria.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.post("/api/turmas/<int:turma_id>/materias/<int:materia_id>/professor")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def atribuir_professor(usuario, turma_id, materia_id):
    """Atribui um professor a uma matéria dentro de uma turma específica."""
    dados = request.get_json(silent=True) or {}
    professor_id = dados.get("professor_id")
    if not professor_id:
        return jsonify({"message": "Campo 'professor_id' é obrigatório."}), 400

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT IGNORE INTO professor_turma_materia (fk_usuario_id, fk_turma_id, fk_materia_id)
            VALUES (%s, %s, %s)
        """, (professor_id, turma_id, materia_id))

        _sincronizar_professor_materia_legado(conexao, professor_id, materia_id)

        conexao.commit()
        return jsonify({"message": "Professor atribuído com sucesso."}), 201

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao atribuir professor.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.delete("/api/turmas/<int:turma_id>/materias/<int:materia_id>/professor/<int:professor_id>")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def remover_professor_materia(usuario, turma_id, materia_id, professor_id):
    """Remove o vínculo de um professor com uma matéria naquela turma."""
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()

        cursor.execute("""
            DELETE FROM professor_turma_materia
            WHERE fk_usuario_id = %s
              AND fk_turma_id = %s
              AND fk_materia_id = %s
        """, (professor_id, turma_id, materia_id))

        _sincronizar_professor_materia_legado(conexao, professor_id, materia_id)

        conexao.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Vínculo não encontrado."}), 404

        return jsonify({"message": "Professor removido da matéria."}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao remover professor.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.put("/api/turmas/<int:turma_id>")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def editar_turma(usuario, turma_id):
    """Edita dados de uma turma existente (período, semestre, turno, capacidade)."""
    import datetime
    dados = request.get_json(silent=True) or {}

    erros = []

    curso_id   = dados.get("curso_id")
    periodo    = dados.get("periodo")
    semestre   = dados.get("semestre")
    turno      = dados.get("turno")
    capacidade = dados.get("capacidade")

    if not curso_id:
        erros.append("Selecione um curso.")
    if not periodo:
        erros.append("Campo 'período' é obrigatório.")
    elif not str(periodo).isdigit() or not (1 <= int(periodo) <= 12):
        erros.append("Período deve ser um número entre 1 e 12.")
    if semestre not in (1, 2, "1", "2"):
        erros.append("Semestre deve ser 1 ou 2.")
    if not turno:
        erros.append("Campo 'turno' é obrigatório.")
    if not capacidade:
        erros.append("Campo 'capacidade' é obrigatório.")
    elif not str(capacidade).isdigit() or not (1 <= int(capacidade) <= 100):
        erros.append("Capacidade deve ser entre 1 e 100.")

    if erros:
        return jsonify({"message": " ".join(erros)}), 400

    curso_id   = int(curso_id)
    periodo    = int(periodo)
    semestre   = int(semestre)
    capacidade = int(capacidade)
    ano        = datetime.date.today().year  # ano sempre fixo no corrente
    turno      = _normalizar_turno(turno)

    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)

        # Verifica se a turma existe
        cursor.execute("SELECT id, turma_letra FROM turma WHERE id = %s AND ativo = 1", (turma_id,))
        turma_atual = cursor.fetchone()
        if not turma_atual:
            return jsonify({"message": "Turma não encontrada."}), 404

        # Busca o curso para montar nome e código
        cursor.execute("SELECT nome, codigo_prefixo FROM curso WHERE id = %s AND ativo = 1", (curso_id,))
        curso = cursor.fetchone()
        if not curso:
            return jsonify({"message": "Curso não encontrado."}), 404

        prefixo     = curso["codigo_prefixo"]
        turno_sigla = turno[0].upper()
        letra       = turma_atual["turma_letra"] or "A"

        codigo = f"{prefixo}-{ano}-{semestre}-{turno_sigla}{letra}"
        nome   = f"{prefixo} {ano}.{semestre} — {turno}{' ' + letra if letra != 'A' else ''}"

        # Verifica conflito de código com OUTRA turma (não a própria)
        prefixo = str(prefixo or "").strip().upper()
        letra_preferida = turma_atual["turma_letra"] or letra
        letra, codigo = _buscar_proxima_letra_turma(
            cursor,
            curso_id=curso_id,
            prefixo=prefixo,
            periodo=periodo,
            ano=ano,
            semestre=semestre,
            turno=turno,
            turma_id_ignorar=turma_id,
            letra_preferida=letra_preferida,
        )
        if not letra:
            return jsonify({"message": "Limite de turmas atingido para esta combinaÃ§Ã£o."}), 409

        nome = _montar_nome_turma(prefixo, ano, semestre, turno, letra)

        cursor.execute("""
            SELECT id FROM turma WHERE codigo = %s AND id != %s
        """, (codigo, turma_id))
        if cursor.fetchone():
            return jsonify({"message": f"Já existe outra turma com o código {codigo}."}), 409

        cursor.execute("""
            UPDATE turma
            SET fk_curso_id = %s, nome = %s, codigo = %s,
                periodo = %s, turma_letra = %s, ano = %s, semestre = %s, turno = %s, capacidade = %s
            WHERE id = %s AND ativo = 1
        """, (curso_id, nome, codigo, periodo, letra, ano, semestre, turno, capacidade, turma_id))

        conexao.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Nenhuma alteração realizada.", "id": turma_id, "nome": nome, "codigo": codigo}), 200

        return jsonify({
            "message": "Turma atualizada com sucesso.",
            "id":     turma_id,
            "nome":   nome,
            "codigo": codigo,
        }), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao editar turma.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@turmas_bp.delete("/api/turmas/<int:turma_id>")
@token_obrigatorio
@papel_obrigatorio("admin", "adm", "coordenador")
def desativar_turma(usuario, turma_id):
    conexao = None
    cursor = None

    try:
        conexao = criar_conexao()
        cursor = conexao.cursor()

        cursor.execute("UPDATE turma SET ativo = 0 WHERE id = %s AND ativo = 1", (turma_id,))
        conexao.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Turma não encontrada."}), 404

        return jsonify({"message": "Turma removida com sucesso."}), 200

    except mysql.connector.Error as erro:
        return jsonify({"message": "Erro ao remover turma.", "erro": str(erro)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()
