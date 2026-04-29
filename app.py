import os, json, time, base64, hmac, hashlib, mysql.connector
from flask import Flask, render_template, request, jsonify, Response
import csv
import io

from login import login_bp
from gestao_usuarios import gestao_usuarios_bp


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static",
)

app.register_blueprint(login_bp)
app.register_blueprint(gestao_usuarios_bp)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "548921"),
        database=os.getenv("DB_NAME", "monitora"),
    )


def base64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def create_jwt(payload):
    header = {"alg": "HS256", "typ": "JWT"}
    header_part = base64url_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    payload_part = base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signature = hmac.new(
        JWT_SECRET.encode("utf-8"),
        f"{header_part}.{payload_part}".encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature_part = base64url_encode(signature)
    return f"{header_part}.{payload_part}.{signature_part}"


def decode_jwt_payload(token):
    try:
        payload_part = token.split(".")[1]
        padding = "=" * (-len(payload_part) % 4)
        decoded = base64.urlsafe_b64decode(payload_part + padding)
        return json.loads(decoded.decode("utf-8"))
    except Exception:
        return None


@app.get("/")
def serve_index():
    return render_template("pages/autentificacao.html")


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    matricula = str(data.get("matricula", "")).strip()
    senha = str(data.get("senha", "")).strip()

    if not matricula or not senha:
        return jsonify({"message": "Informe matrícula e senha."}), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT matricula, papel
            FROM usuario
            WHERE matricula = %s AND senha = %s
            """,
            (matricula, senha),
        )
        user = cursor.fetchone()
    except mysql.connector.Error as error:
        print(f"Erro no banco: {error}")
        return jsonify({"message": "Erro ao conectar com o banco de dados."}), 500
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

    if not user:
        print(f"Login recusado para matrícula {matricula}")
        return jsonify({"message": "Matrícula ou senha inválidas."}), 401

    now = int(time.time())
    token = create_jwt(
        {
            "sub": str(user["matricula"]),
            "matricula": user["matricula"],
            "papel": user["papel"],
            "iat": now,
            "exp": now + JWT_EXPIRES_IN,
        }
    )

    print(f"Login aceito para matrícula {user['matricula']}")
    print(f"JWT gerado: {token}")
    print(f"Payload do JWT: {decode_jwt_payload(token)}")
    print(
        "Usuário autenticado:",
        {"matricula": user["matricula"], "papel": user["papel"]},
    )

    return jsonify(
        {
            "message": "Login realizado com sucesso.",
            "token": token,
            "matricula": user["matricula"],
            "papel": user["papel"],
            "usuario": {
                "matricula": user["matricula"],
                "papel": user["papel"],
            },
        }
    )

@app.route("/frequencia")
def frequencia():
    aluno_id = request.args.get("aluno")
    materia_id = request.args.get("materia")
    periodo_id = request.args.get("periodo")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # sempre busca alunos pro select
    cursor.execute("SELECT id, nome FROM usuario")
    alunos = cursor.fetchall()

    aluno = None
    materia = None
    periodo = None
    mostrar = False

    if aluno_id and materia_id:

        cursor.execute("""
        SELECT 
            u.id,
            u.nome,
            COUNT(f.id) AS total,
            COALESCE(SUM(f.presente = 1), 0) AS presencas,
            COALESCE(SUM(f.presente = 0), 0) AS faltas
        FROM usuario u
        LEFT JOIN frequencia f ON f.fk_usuario_id = u.id
        WHERE u.id = %s
        GROUP BY u.id, u.nome
    """, (aluno_id,))

        result = cursor.fetchone()

        if result:
            total = result["total"] or 0
            presencas = result["presencas"] or 0
            faltas = result["faltas"] or 0
            percentual = f"{round((presencas / total) * 100)}%" if total > 0 else "0%"

            aluno = {
                "nome": result["nome"],
                "total": total,
                "presencas": presencas,
                "faltas": faltas,
                "presenca": percentual
            }

            mostrar = True

    nomes_materias = {
        "1": "Banco de Dados",
        "2": "Algoritmos",
        "3": "Estrutura de Dados"
    }

    nomes_periodos = {
        "5": "5º período",
        "6": "6º período"
    }

    materia = nomes_materias.get(materia_id)
    periodo = nomes_periodos.get(periodo_id)

    cursor.close()
    connection.close()

    return render_template(
        "pages/frequencia.html",
        alunos=alunos,
        mostrar=mostrar,
        aluno=aluno,
        materia=materia,
        periodo=periodo
    )


@app.route("/frequencia/relatorio")
def relatorio_frequencia():
    aluno_id = request.args.get("aluno")
    materia_id = request.args.get("materia")
    periodo_id = request.args.get("periodo")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    aluno = None

    if aluno_id and materia_id:

        cursor.execute("""
            SELECT 
                u.nome,
                COUNT(f.id) AS total,
                SUM(f.presente = 1) AS presencas,
                SUM(f.presente = 0) AS faltas
            FROM frequencia f
            JOIN usuario u ON u.id = f.fk_usuario_id
            JOIN materia m ON m.id = f.fk_materia_id
            WHERE u.id = %s AND m.id = %s
        """, (aluno_id, materia_id))

        result = cursor.fetchone()

        if result:
            total = result["total"] or 0
            presencas = result["presencas"] or 0
            faltas = result["faltas"] or 0

            percentual = f"{round((presencas / total) * 100)}%" if total > 0 else "0%"

            aluno = {
                "nome": result["nome"],
                "total": total,
                "presencas": presencas,
                "faltas": faltas,
                "presenca": percentual
            }

    cursor.close()
    connection.close()

    nomes_materias = {
        "1": "Banco de Dados",
        "2": "Algoritmos",
        "3": "Estrutura de Dados"
    }

    nomes_periodos = {
        "5": "5º período",
        "6": "6º período"
    }

    materia = nomes_materias.get(materia_id)
    periodo = nomes_periodos.get(periodo_id)

    conteudo = f"""
RELATÓRIO DE FREQUÊNCIA

Aluno: {aluno['nome'] if aluno else 'N/A'}
Matéria: {materia}
Período: {periodo}

Total de aulas: {aluno['total'] if aluno else 0}
Presenças: {aluno['presencas'] if aluno else 0}
Faltas: {aluno['faltas'] if aluno else 0}
Frequência: {aluno['presenca'] if aluno else '0%'}
"""

    return Response(
        conteudo,
        mimetype="text/plain",
        headers={
            "Content-Disposition": "attachment; filename=relatorio_frequencia.txt"
        }
    )

if __name__ == "__main__":
    app.run(debug=True)