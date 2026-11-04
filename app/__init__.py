import os
from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "lab4-dev-only-secret")
app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024

from . import views
from .users import users_bp
from .products import products_bp

app.register_blueprint(users_bp)
app.register_blueprint(products_bp)


def create_app():
    return app
