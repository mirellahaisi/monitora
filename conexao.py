import os
import mysql.connector


def criar_conexao():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "548921"),
        database=os.getenv("DB_NAME", "monitora"),
    )