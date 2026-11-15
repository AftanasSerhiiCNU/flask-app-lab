import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .config import config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("APP_CONFIG", "development")

    if config_name not in config:
        raise ValueError(f"Невідомий режим конфігурації: {config_name}")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    if not app.config.get("SECRET_KEY"):
        if config_name == "testing":
            app.config["SECRET_KEY"] = "testing-only-secret"
        else:
            raise RuntimeError("Необхідно встановити SECRET_KEY у файлі .env")

    db.init_app(app)
    migrate.init_app(app, db)

    from .views import register_routes
    from .users import users_bp
    from .products import products_bp
    from .posts import post_bp
    from .posts.models import Post

    register_routes(app)

    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(post_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html", title="Сторінку не знайдено"), 404

    return app
