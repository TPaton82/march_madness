import os
from flask import Flask
from flask_migrate import Migrate, upgrade as migrate_upgrade
from app.auth.routes import auth_bp
from app.bracket.routes import bracket_bp
from app.extensions.db import db
from app.scoreboard.routes import scoreboard_bp
from app.rules.routes import rules_bp
from app.games.routes import games_bp
from app.admin.routes import admin_bp


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    app.secret_key = os.environ.get("FLASK_SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # init database
    db.init_app(app)
    migrate = Migrate(app, db)
    from app.extensions import models

    with app.app_context():
        # Run migrations automatically
        migrate_upgrade()

        # Optional: Only seed if table empty
        from app.extensions.models import Team
        from app.extensions.seed import seed_teams, seed_round_1, seed_future_rounds

        if Team.query.count() == 0:
            teams = seed_teams()
            seed_round_1(teams)
            seed_future_rounds()

    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(bracket_bp)
    app.register_blueprint(scoreboard_bp)
    app.register_blueprint(rules_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(admin_bp)


    return app
