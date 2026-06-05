from datetime import date, datetime
import hmac

from werkzeug.security import check_password_hash, generate_password_hash


HASH_PREFIXOS = ("pbkdf2:", "scrypt:")


def _coagir_data(valor):
    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    texto = str(valor or "").strip()
    if not texto:
        return None

    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except ValueError:
        return None


def senha_esta_hash(valor):
    return str(valor or "").startswith(HASH_PREFIXOS)


def gerar_hash_senha(senha):
    return generate_password_hash(str(senha or ""))


def verificar_senha(senha_informada, senha_armazenada):
    senha_digitada = str(senha_informada or "")
    senha_salva = str(senha_armazenada or "")

    if not senha_salva:
        return False

    if senha_esta_hash(senha_salva):
        try:
            return check_password_hash(senha_salva, senha_digitada)
        except ValueError:
            return False

    return hmac.compare_digest(senha_salva, senha_digitada)


def senha_precisa_upgrade(senha_armazenada):
    senha_salva = str(senha_armazenada or "")
    return bool(senha_salva) and not senha_esta_hash(senha_salva)


def senha_padrao_data_nascimento(data_nascimento):
    data_base = _coagir_data(data_nascimento)
    if not data_base:
        raise ValueError("Data de nascimento invalida para gerar senha padrao.")

    return data_base.strftime("%d%m%y")
