import os
import hashlib
from functools import wraps
from flask import redirect, url_for, session, current_app
from app.extensions.constants import REGIONS
from app.extensions.models import get_bracket_data_for_region


def create_secure_password(password, secret_key, hash_algo="sha256", iterations=100000):
    salt = os.urandom(16)

    hash_value = hashlib.pbkdf2_hmac(hash_algo, password.encode("utf-8") + secret_key.encode("utf-8"), salt, iterations)

    password_hash = salt + hash_value

    return password_hash[:16], password_hash[16:], hash_algo, iterations


def logged_in(func):
    @wraps(func)
    def check_logged_in(*args, **kwargs):
        # Only show the page if user is logged in
        if "loggedin" in session:
            return func(*args, **kwargs)

        # User is not loggedin so redirect to login page
        return redirect("/login")

    return check_logged_in


def get_team_logo(team_name):
    """Return the static URL for team logo, preferring SVG, falling back to PNG."""
    svg_path = os.path.join(current_app.static_folder, "images/team_logos", f"{team_name}.svg")
    png_path = os.path.join(current_app.static_folder, "images/team_logos", f"{team_name}.png")

    if os.path.exists(svg_path):
        return url_for("static", filename=f"images/team_logos/{team_name}.svg")

    elif os.path.exists(png_path):
        return url_for("static", filename=f"images/team_logos/{team_name}.png")

    else:
        return url_for("static", filename="images/team_logos/placeholder.png")


def create_users_bracket_data(user_picks, team_names, winners):
    """Create users bracket data"""
    bracket_data = {}
    lost_teams = set()
    for region in REGIONS:
        rounds = get_bracket_data_for_region(region)

        for round, games in rounds.items():
            for game in games:
                game_id = game["game_id"]
                # Insert the users pick and actual winner
                actual_winner_id = winners.get(game_id)
                game["actual_winner_id"] = actual_winner_id

                predicted_winner = user_picks.get(game_id)
                game["predicted_winner_id"] = predicted_winner

                # Determine correctness
                # Determine per-team correctness
                game["team_1_correct"] = True
                game["team_2_correct"] = True

                # If we're not in round 1, we need to insert the team names
                if round != 1:
                    user_pick_1 = user_picks.get(game["source_game_1"])
                    if user_pick_1:
                        winner_1, seed_1 = user_pick_1
                        game["team_1_name"] = team_names.get(winner_1)
                        game["team_1_seed"] = seed_1
                        game["team_1_id"] = winner_1

                        # Mark lost if upstream or incorrect
                        if winner_1 in lost_teams:
                            game["team_1_correct"] = False

                    user_pick_2 = user_picks.get(game["source_game_2"])
                    if user_pick_2:
                        winner_2, seed_2 = user_pick_2
                        game["team_2_name"] = team_names.get(winner_2)
                        game["team_2_seed"] = seed_2
                        game["team_2_id"] = winner_2

                        if winner_2 in lost_teams:
                            game["team_2_correct"] = False

                # Mark predicted winner lost if it doesn't match actual winner
                if predicted_winner and actual_winner_id and predicted_winner[0] != actual_winner_id:
                    lost_teams.add(predicted_winner[0])
                    if "team_1_id" in game and game["team_1_id"] == predicted_winner[0]:
                        game["team_1_correct"] = False
                    if "team_2_id" in game and game["team_2_id"] == predicted_winner[0]:
                        game["team_2_correct"] = False

        bracket_data[region.replace(" ", "_").lower()] = rounds

    return bracket_data
