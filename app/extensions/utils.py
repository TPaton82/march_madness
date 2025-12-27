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
        return url_for("static", filename="images/team_logos/placeholder.svg")

def update_game_state(game, user_pick, source_game_num, team_names):
    """Update the state of a game"""
    pick_id, pick_seed = user_pick
    pick_name = team_names.get(pick_id)

    # No winner in previous game yet, fill with user picks
    if game[f"team_{source_game_num}_name"] is None:
        game[f"team_{source_game_num}_name"] = team_names.get(pick_id)
        game[f"team_{source_game_num}_seed"] = pick_seed
        game[f"team_{source_game_num}_id"] = pick_id

    # If the user has picked correctly
    elif pick_name == game[f"team_{source_game_num}_name"]:
        game[f"team_{source_game_num}_state"] = "correct"

    # Or the user has picked incorrectly
    else:
        game[f"team_{source_game_num}_state"] = "incorrect"

        # Set the current team to the correct team
        game[f"correct_{source_game_num}_name"] = game[f"team_{source_game_num}_name"]
        game[f"correct_{source_game_num}_seed"] = game[f"team_{source_game_num}_seed"]

        # Now replace the current team with the user pick
        game[f"team_{source_game_num}_name"] = pick_name
        game[f"team_{source_game_num}_seed"] = pick_seed
        game[f"team_{source_game_num}_id"] = pick_id

    return game

def create_users_bracket_data(user_picks, team_names):
    """Create users bracket data"""
    bracket_data = {}
    for region in REGIONS:
        rounds = get_bracket_data_for_region(region)

        for round, games in rounds.items():
            for game in games:
                game_id = game["game_id"]

                predicted_winner = user_picks.get(game_id)
                game["predicted_winner_id"] = predicted_winner

                # If we're not in round 1, we need to calculate the state
                if round != 1:
                    user_pick_1 = user_picks.get(game["source_game_1"])
                    if user_pick_1:
                        update_game_state(game, user_pick_1, 1, team_names)

                    user_pick_2 = user_picks.get(game["source_game_2"])
                    if user_pick_2:
                        update_game_state(game, user_pick_2, 2, team_names)

        bracket_data[region.replace(" ", "_").lower()] = rounds

    return bracket_data
