from flask import Blueprint, render_template, request, session, url_for, redirect, jsonify
from app.extensions.db import (
    get_bracket_data_for_region,
    create_user_picks,
    add_user_winner_pick,
    add_user_final_score,
    get_user_winner_pick,
    get_user_final_score,
    reset_user_picks,
    get_user_picks,
    get_team_names,
)
from app.extensions.utils import logged_in, get_team_logo
from app.extensions.constants import REGIONS

bracket_bp = Blueprint("bracket", __name__)


def create_users_bracket_data(user_picks, team_names):
    """Create users bracket data"""
    bracket_data = {}
    for region in REGIONS:
        rounds = get_bracket_data_for_region(region)

        for round, games in rounds.items():
            for game in games:
                # Insert the users pick
                game["predicted_winner_id "] = user_picks.get(game["game_id"])

                # If we're not in round 1, we need to insert the team names
                if round != 1:
                    user_pick_1 = user_picks.get(game["source_game_1"])
                    if user_pick_1:
                        winner_1, seed_1 = user_pick_1
                        game["team_1_name"] = team_names.get(winner_1)
                        game["team_1_seed"] = seed_1
                        game["team_1_id"] = winner_1

                    user_pick_2 = user_picks.get(game["source_game_2"])
                    if user_pick_2:
                        winner_2, seed_2 = user_pick_2
                        game["team_2_name"] = team_names.get(winner_2)
                        game["team_2_seed"] = seed_2
                        game["team_2_id"] = winner_2

        bracket_data[region.replace(" ", "_").lower()] = rounds

    return bracket_data


@bracket_bp.route("/bracket", methods=["GET"])
@logged_in
def bracket():
    """Create bracket page"""
    user_id = session["user_id"]
    user_picks = get_user_picks(user_id)
    winner = get_user_winner_pick(user_id)
    final_score = get_user_final_score(user_id)
    team_names = get_team_names()
    bracket_data = create_users_bracket_data(user_picks, team_names)

    return render_template(
        "bracket.html",
        **bracket_data,
        winner=winner,
        final_score=final_score,
        user_picks=user_picks,
        get_team_logo=get_team_logo,
    )


@bracket_bp.route("/submit-picks", methods=["POST"])
def submit_picks():
    """Submit user picks."""
    user_id = session["user_id"]
    data = request.get_json()
    user_picks = data.get("user_picks", [])
    winner_pick = data.get("winner_pick")
    final_score = data.get("final_score")

    create_user_picks(user_id, user_picks)

    if winner_pick:
        add_user_winner_pick(user_id, winner_pick)

    if final_score:
        try:
            final_score = int(final_score)
        except ValueError:
            return jsonify({"success": False, "message": "Final score must be a number"})

        add_user_final_score(user_id, final_score)

    return jsonify({"success": True, "message": "Picks saved!"})


@bracket_bp.route("/reset-picks", methods=["POST"])
def reset_picks():
    """Reset user picks."""
    user_id = session["user_id"]
    reset_user_picks(user_id)
    return redirect(url_for("bracket.bracket"))
