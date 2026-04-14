import base64
import hashlib
import hmac
import json
import os
import time

import mysql.connector
from flask import Flask, jsonify, render_template, request


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JWT_SECRET = os.getenv("JWT_SECRET", "monitora-dev-secret")
JWT_EXPIRES_IN = int(os.getenv("JWT_EXPIRES_IN", "3600"))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static",
)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost:3306"),
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
    return render_template("pages/frequencia.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
