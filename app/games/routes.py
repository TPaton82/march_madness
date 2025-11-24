from flask import Blueprint, render_template
from app.extensions.utils import logged_in, get_team_logo
from app.extensions.db import get_upcoming_games_with_picks

games_bp = Blueprint("games", __name__)


def format_upcoming_games(upcoming_games):
    """Format the upcoming games for display"""
    games = {}
    for row in upcoming_games:
        game_id = row["game_id"]
        if game_id not in games:
            games[game_id] = {
                "game_id": game_id,
                "round": row["round"],
                "game_time": row["game_time"],
                "team_1_id": row["team_1_id"],
                "team_1_name": row["team_1_name"],
                "team_1_seed": row["team_1_seed"],
                "team_2_id": row["team_2_id"],
                "team_2_name": row["team_2_name"],
                "team_2_seed": row["team_2_seed"],
                "team_1_pickers": [],
                "team_2_pickers": [],
            }

        # Add pickers
        if row["predicted_winner_id"] == row["team_1_id"]:
            games[game_id]["team_1_pickers"].append(row["name"].title())
        elif row["predicted_winner_id"] == row["team_2_id"]:
            games[game_id]["team_2_pickers"].append(row["name"].title())

    return list(games.values())


@games_bp.route("/games", methods=["GET"])
@logged_in
def games():
    upcoming_games = get_upcoming_games_with_picks()
    formatted_games = format_upcoming_games(upcoming_games)

    return render_template("games.html", games=formatted_games, get_team_logo=get_team_logo)
