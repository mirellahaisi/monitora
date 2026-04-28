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


def base64url_decode(dados):
    padding = "=" * (-len(dados) % 4)
    return base64.urlsafe_b64decode(dados + padding)


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


def validar_token(token):
    try:
        partes = token.split(".")

        if len(partes) != 3:
            return None

        header_codificado, payload_codificado, assinatura_recebida = partes

        assinatura = hmac.new(
            JWT_SECRET.encode("utf-8"),
            f"{header_codificado}.{payload_codificado}".encode("utf-8"),
            hashlib.sha256
        ).digest()

        assinatura_correta = base64url_encode(assinatura)

        if not hmac.compare_digest(assinatura_recebida, assinatura_correta):
            return None

        payload = json.loads(
            base64url_decode(payload_codificado).decode("utf-8")
        )

        if payload.get("exp") < int(time.time()):
            return None

        return payload

    except Exception:
        return None