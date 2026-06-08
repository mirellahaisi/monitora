import os
import json
import time
import base64
import hmac
import hashlib
import mysql.connector

from flask import Flask, render_template, request, jsonify

from .login import login_bp
from .gestao_usuarios import gestao_usuarios_bp
from .notas import notas_bp
from .frequencia import frequencia_bp
from .turmas import turmas_bp
from .calendario import calendario_bp
from .presenca import presenca_bp
from .mensagens import mensagens_bp
from .cursos import cursos_bp
from .materias import materias_bp

 


# ========================
# CONFIGS JWT
# ========================
JWT_SECRET = "monitora_chave_mlg_2026"
JWT_EXPIRES_IN = 3600

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "static"),
    static_url_path="/static",
)

# ========================
# BLUEPRINTS
# ========================
app.register_blueprint(login_bp)
app.register_blueprint(gestao_usuarios_bp)
app.register_blueprint(notas_bp)
app.register_blueprint(frequencia_bp)
app.register_blueprint(presenca_bp)
app.register_blueprint(turmas_bp)
app.register_blueprint(calendario_bp)
app.register_blueprint(mensagens_bp)
app.register_blueprint(cursos_bp)
app.register_blueprint(materias_bp)


# ========================
# BANCO
# ========================
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
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

    return f"{header_part}.{payload_part}.{base64url_encode(signature)}"


def decode_jwt_payload(token):
    try:
        payload_part = token.split(".")[1]
        padding = "=" * (-len(payload_part) % 4)
        decoded = base64.urlsafe_b64decode(payload_part + padding)
        return json.loads(decoded.decode())
    except Exception:
        return None

# ========================
# ROTAS
# ========================


@app.get("/login")
def serve_login():
    return render_template("pages/autentificacao.html")


@app.get("/")
def serve_index():
    return render_template("pages/index.html")


@app.post("/api/login-legado")
def login_legado():
    data = request.get_json(silent=True) or {}

    matricula = data.get("matricula")
    senha = data.get("senha")

    if not matricula or not senha:
        return jsonify({"message": "Informe matrícula e senha."}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, matricula, papel, nome, email FROM usuario WHERE matricula=%s AND senha=%s",
        (matricula, senha),
    )
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user:
        return jsonify({"message": "Matrícula ou senha inválidas."}), 401

    now = int(time.time())
    token = create_jwt({
        "id":        user["id"],
        "matricula": user["matricula"],
        "papel":     user["papel"],
        "nome":      user["nome"],
        "email":     user.get("email", ""),
        "iat":       now,
        "exp":       now + JWT_EXPIRES_IN,
    })

    return jsonify({
        "message": "Login realizado com sucesso",
        "token":   token,
        "usuario": user,
    })



@app.get("/mensagens")
def serve_mensagens():
    return render_template("pages/mensagens.html", active_page="mensagens")

# ========================
# RUN
# ========================
if __name__ == "__main__":
    app.run(debug=True)
