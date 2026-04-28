import base64
import hashlib
import hmac
import json
import os
import time


JWT_SECRET = os.getenv("JWT_SECRET", "monitora-dev-secret")
TEMPO_SESSAO = int(os.getenv("JWT_EXPIRES_IN", "3600"))


def base64url_encode(dados):
    return base64.urlsafe_b64encode(dados).rstrip(b"=").decode("utf-8")


def gerar_token(usuario):
    agora = int(time.time())

    header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    payload = {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "papel": usuario["papel"],
        "iat": agora,
        "exp": agora + TEMPO_SESSAO
    }

    header_codificado = base64url_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )

    payload_codificado = base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )

    assinatura = hmac.new(
        JWT_SECRET.encode("utf-8"),
        f"{header_codificado}.{payload_codificado}".encode("utf-8"),
        hashlib.sha256
    ).digest()

    assinatura_codificada = base64url_encode(assinatura)

    token = f"{header_codificado}.{payload_codificado}.{assinatura_codificada}"

    return token, payload