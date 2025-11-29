
from flask import Blueprint, render_template, session, request, redirect, abort
from sqlalchemy.orm import aliased

from app.extensions.utils import logged_in, get_team_logo
from app.extensions.models import Game, Team
from app.extensions.db import db
admin_bp = Blueprint("admin", __name__)


def update_game_winner(game_id, winner_id):
    """Update winner for a given game"""
    game = db.session.get(Game, game_id)

    # 1. Update the winner
    game.winner_id = winner_id

    # 2. Find child games where this game feeds into
    child_games = Game.query.filter(
        (Game.source_game_1 == game_id) | (Game.source_game_2 == game_id)
    ).all()

    # 3. Update the correct team slot in each child game
    for child in child_games:
        if child.source_game_1 == int(game_id):
            child.team_1_id = winner_id

        if child.source_game_2 == int(game_id):
            child.team_2_id = winner_id

    db.session.commit()


def get_all_games():
    """Fetch all games"""
    team_1 = aliased(Team)
    team_2 = aliased(Team)

    games = (
        db.session.query(
            Game.game_id,
            Game.round,
            Game.team_1_id,
            team_1.name.label("team_1_name"),
            Game.team_2_id,
            team_2.name.label("team_2_name"),
            Game.winner_id
        )
        .outerjoin(team_1, Game.team_1_id == team_1.team_id)
        .outerjoin(team_2, Game.team_2_id == team_2.team_id)
        .order_by(Game.round, Game.game_id)
        .all()
    )
    
    return games


@admin_bp.route('/admin', methods=['GET', 'POST'])
@logged_in
def admin():
    user_name = session["user_name"]

    if user_name.lower() != "tom":
        abort(403)
    
    if request.method == "POST":
        game_id = request.form.get("game_id")
        winner_id = request.form.get("winner_id") or None
        update_game_winner(game_id, winner_id)
        return redirect("/admin")

    games = get_all_games()

    return render_template('admin.html', games=games, get_team_logo=get_team_logo)
