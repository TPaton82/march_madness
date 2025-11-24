import os
from flask import Flask
from app.extensions.db import mysql
from app.extensions.utils import get_cloud_secret
from app.auth.routes import auth_bp
from app.bracket.routes import bracket_bp
from app.scoreboard.routes import scoreboard_bp
from app.rules.routes import rules_bp
from app.games.routes import games_bp
from app.admin.routes import admin_bp

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # MySQL config (Cloud or local)
    if os.environ.get("GAE_ENV") == "standard":
        app.secret_key = get_cloud_secret("MARCH_MADNESS_KEY")
        app.config["MYSQL_UNIX_SOCKET"] = f"/cloudsql/{get_cloud_secret('CLOUD_SQL_CONNECTION_NAME')}"
        app.config["MYSQL_USER"] = get_cloud_secret("CLOUD_SQL_USERNAME")
        app.config["MYSQL_PASSWORD"] = get_cloud_secret("CLOUD_SQL_PASSWORD")
        app.config["MYSQL_DB"] = get_cloud_secret("CLOUD_SQL_MM_DATABASE_NAME")
    else:
        app.secret_key = "SECRET_KEY"
        app.config["MYSQL_HOST"] = "localhost"
        app.config["MYSQL_USER"] = "root"
        app.config["MYSQL_PASSWORD"] = "password"
        app.config["MYSQL_DB"] = "march_madness"

    # init database
    mysql.init_app(app)

    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(bracket_bp)
    app.register_blueprint(scoreboard_bp)
    app.register_blueprint(rules_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(admin_bp)

    return app