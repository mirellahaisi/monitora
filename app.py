import os, json, time, base64, hmac, hashlib, mysql.connector
from flask import Flask, render_template, request, jsonify, Response

from login import login_bp
from gestao_usuarios import gestao_usuarios_bp
from notas import notas_bp

# CONFIGS JWT (adicionei pq tava faltando)
JWT_SECRET = "segredo_super_secreto"
JWT_EXPIRES_IN = 3600

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static",
)

# BLUEPRINTS
app.register_blueprint(login_bp)
app.register_blueprint(gestao_usuarios_bp)
app.register_blueprint(notas_bp)

# ========================
# BANCO
# ========================
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "548921"),
        database=os.getenv("DB_NAME", "monitora"),
    )

# ========================
# JWT
# ========================
def base64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def create_jwt(payload):
    header = {"alg": "HS256", "typ": "JWT"}

    header_part = base64url_encode(json.dumps(header).encode())
    payload_part = base64url_encode(json.dumps(payload).encode())

    signature = hmac.new(
        JWT_SECRET.encode(),
        f"{header_part}.{payload_part}".encode(),
        hashlib.sha256,
    ).digest()

    signature_part = base64url_encode(signature)

    return f"{header_part}.{payload_part}.{signature_part}"

def decode_jwt_payload(token):
    try:
        payload_part = token.split(".")[1]
        padding = "=" * (-len(payload_part) % 4)
        decoded = base64.urlsafe_b64decode(payload_part + padding)
        return json.loads(decoded.decode())
    except:
        return None

# ========================
# ROTAS
# ========================

@app.get("/")
def serve_index():
    return render_template("pages/autentificacao.html")


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}

    matricula = data.get("matricula")
    senha = data.get("senha")

    if not matricula or not senha:
        return jsonify({"message": "Informe matrícula e senha."}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT matricula, papel FROM usuario WHERE matricula=%s AND senha=%s",
        (matricula, senha),
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if not user:
        return jsonify({"message": "Matrícula ou senha inválidas."}), 401

    now = int(time.time())

    token = create_jwt({
        "matricula": user["matricula"],
        "papel": user["papel"],
        "iat": now,
        "exp": now + JWT_EXPIRES_IN,
    })

    return jsonify({
        "message": "Login realizado com sucesso",
        "token": token,
        "usuario": user
    })


# ========================
# FREQUÊNCIA
# ========================
@app.route("/frequencia")
def frequencia():
    aluno_id = request.args.get("aluno")
    materia_id = request.args.get("materia")
    periodo_id = request.args.get("periodo")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT id, nome FROM usuario")
    alunos = cursor.fetchall()

    aluno = None
    mostrar = False

    if aluno_id and materia_id:
        cursor.execute("""
            SELECT 
                u.nome,
                COUNT(f.id) AS total,
                COALESCE(SUM(f.presente = 1), 0) AS presencas,
                COALESCE(SUM(f.presente = 0), 0) AS faltas
            FROM usuario u
            LEFT JOIN frequencia f ON f.fk_usuario_id = u.id
            WHERE u.id = %s
            GROUP BY u.nome
        """, (aluno_id,))

        result = cursor.fetchone()

        if result:
            total = result["total"]
            presencas = result["presencas"]
            faltas = result["faltas"]

            percentual = f"{round((presencas / total) * 100)}%" if total else "0%"

            aluno = {
                "nome": result["nome"],
                "total": total,
                "presencas": presencas,
                "faltas": faltas,
                "presenca": percentual
            }

            mostrar = True

    materia_map = {
        "1": "Banco de Dados",
        "2": "Algoritmos",
        "3": "Estrutura de Dados"
    }

    periodo_map = {
        "5": "5º período",
        "6": "6º período"
    }

    cursor.close()
    connection.close()

    return render_template(
        "pages/frequencia.html",
        alunos=alunos,
        mostrar=mostrar,
        aluno=aluno,
        materia=materia_map.get(materia_id),
        periodo=periodo_map.get(periodo_id)
    )


# ========================
# RELATÓRIO
# ========================
@app.route("/frequencia/relatorio")
def relatorio_frequencia():
    aluno_id = request.args.get("aluno")
    materia_id = request.args.get("materia")
    periodo_id = request.args.get("periodo")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT nome FROM usuario WHERE id=%s", (aluno_id,))
    aluno = cursor.fetchone()

    cursor.execute("""
        SELECT 
            COUNT(id) AS total,
            COALESCE(SUM(presente = 1), 0) AS presencas,
            COALESCE(SUM(presente = 0), 0) AS faltas
        FROM frequencia
        WHERE fk_usuario_id=%s AND fk_materia_id=%s
    """, (aluno_id, materia_id))

    freq = cursor.fetchone()

    cursor.close()
    connection.close()

    total = freq["total"]
    presencas = freq["presencas"]
    faltas = freq["faltas"]

    percentual = f"{round((presencas / total) * 100)}%" if total else "0%"

    conteudo = f"""
RELATÓRIO DE FREQUÊNCIA

Aluno: {aluno['nome']}
Total: {total}
Presenças: {presencas}
Faltas: {faltas}
Frequência: {percentual}
"""

    return Response(
        conteudo,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=relatorio.txt"}
    )


# ========================
# RUN
# ========================
if __name__ == "__main__":
    app.run(debug=True)