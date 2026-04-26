import os
from flask import Flask

from login import login_bp


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static",
)

app.register_blueprint(login_bp)


if __name__ == "__main__":
    app.run(debug=True)