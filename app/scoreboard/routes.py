from collections import defaultdict
from flask import Blueprint, render_template
from app.extensions.db import get_all_users, get_completed_games, get_user_picks, get_all_games, get_team_name_from_id
from app.extensions.utils import logged_in, get_team_logo
from app.extensions.constants import ROUND_POINTS


scoreboard_bp = Blueprint("scoreboard", __name__)


def calculate_scoreboard():
    """Calculate the current scoreboard"""
    users = get_all_users()

    picks_by_user = {}
    for user in users:
        user_picks = get_user_picks(user["user_id"])
        picks_by_user[user["name"]] = user_picks

    completed_games = get_completed_games()

    scoreboard = []
    for user_name, user_picks in picks_by_user.items():
        user_round_scores = defaultdict(int)
        total_correct = 0
        current_points = 0
        maximum_points = 0

        # 1: Calculate current points
        for game_id, (user_pick, pick_seed) in user_picks.items():
            if game_id in completed_games:
                actual = completed_games[game_id]
                round_num = actual["round"]
                if user_pick == actual["winner_id"]:
                    points = ROUND_POINTS[round_num] + pick_seed
                    current_points += points
                    user_round_scores[round_num] += points
                    total_correct += 1

        # 2: Calculate maximum possible remaining points
        all_games = get_all_games()

        for game in all_games:
            game_id = game["game_id"]
            round = game["round"]
            predicted_pick, predicted_seed = user_picks.get(game_id, (None, None))

            # Already scored
            if game["winner_id"] is not None:
                continue

            # If predicted team still alive, add points
            if predicted_pick and predicted_pick in [game["team_1_id"], game["team_2_id"]]:
                maximum_points += ROUND_POINTS[round] + predicted_seed

        predicted_champion = get_team_name_from_id(user["winner_id"])

        scoreboard.append(
            {
                "username": user_name.title(),
                "current_points": current_points,
                "max_points": current_points + maximum_points,
                "correct_picks": total_correct,
                "round_scores": user_round_scores,
                "predicted_champion_name": predicted_champion,
                "predicted_final_score": user["final_score"],
            }
        )

    return scoreboard


@scoreboard_bp.route("/scoreboard", methods=["GET"])
@logged_in
def scoreboard():
    """Render the scoreboard"""
    scoreboard = calculate_scoreboard()

    return render_template("scoreboard.html", scoreboard=scoreboard, get_team_logo=get_team_logo)
