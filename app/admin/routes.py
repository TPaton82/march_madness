
from flask import Blueprint, render_template, session, request, redirect, abort
from app.extensions.utils import logged_in, get_team_logo
from app.extensions.db import update_game_winner, get_all_games

admin_bp = Blueprint("admin", __name__)


@admin_bp.route('/admin', methods=['GET', 'POST'])
@logged_in
def admin():
    user_id = session["user_id"]

    if user_id != 1:
        abort(403)
    
    if request.method == "POST":
        game_id = request.form.get("game_id")
        winner_id = request.form.get("winner_id") or None
        update_game_winner(game_id, winner_id)
        return redirect("/admin")

    games = get_all_games()

    return render_template('admin.html', games=games, get_team_logo=get_team_logo)
