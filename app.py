import os

from flask import Flask, render_template
from login import login_bp
from gestao_usuarios import gestao_usuarios_bp
from notas import notas_bp
from frequencia import frequencia_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static",
)

app.register_blueprint(login_bp)
app.register_blueprint(gestao_usuarios_bp)
app.register_blueprint(notas_bp)
app.register_blueprint(frequencia_bp)

@app.get("/")
def index():
    """Página pública de apresentação — sempre abre aqui."""
    return render_template("pages/index.html")


if __name__ == "__main__":
    app.run(debug=True)