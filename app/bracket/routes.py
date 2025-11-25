from collections import defaultdict
from flask import Blueprint, render_template, request, session, url_for, redirect, jsonify
from sqlalchemy.orm import aliased
from app.extensions.models import User, UserPick, Game, Team
from app.extensions.utils import logged_in, get_team_logo
from app.extensions.constants import REGIONS
from app.extensions.db import db

bracket_bp = Blueprint("bracket", __name__)


def get_bracket_data_for_region(region):
    """Fetch all bracket data"""
    team_1 = aliased(Team)
    team_2 = aliased(Team)

    bracket_data = (
        db.session.query(
            Game.game_id,
            Game.round,
            Game.source_game_1,
            Game.source_game_2,
            Game.team_1_id,
            Game.team_2_id,
            team_1.name.label("team_1_name"),
            team_1.seed.label("team_1_seed"),
            team_2.name.label("team_2_name"),
            team_2.seed.label("team_2_seed"),
            Game.winner_id,
            Game.region,
            Game.game_time,
        )
        .outerjoin(team_1, Game.team_1_id == team_1.team_id)
        .outerjoin(team_2, Game.team_2_id == team_2.team_id)
        .filter(Game.region == region)
        .order_by(Game.round, Game.round_order)
    ).all()

    # # Group games by round for easier rendering in the template
    rounds = defaultdict(list)

    for game in bracket_data:
        rounds[game.round].append(dict(game._mapping))

    return rounds


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


def get_user_picks(user_id: int):
    """Getch user picks."""

    raw_picks = (
        db.session.query(
            UserPick.game_id,
            UserPick.predicted_winner_id,
            Team.seed
        )
        .join(Team, UserPick.predicted_winner_id == Team.team_id)
        .filter(UserPick.user_id == user_id)
    ).all()
    
    user_picks = {pick.game_id: (pick.predicted_winner_id, pick.seed) for pick in raw_picks}

    return user_picks


def get_user_winner_pick(user_id):
    """get user winner pick"""
    user = db.session.get(User, user_id)
    team = db.session.get(Team, user.winner_id)

    if team is None:
        return None

    return {
        "team_id": team.team_id,
        "seed": team.seed,
        "name": team.name
    }


def get_user_final_score(user_id):
    """get user final score"""
    user = db.session.get(User, user_id)
    return {"value": user.final_score}


def get_team_names():
    """Fetch all team names"""
    raw_teams = Team.query.all()
    teams = {team.team_id: team.name for team in raw_teams}
    return teams


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


def create_user_picks(user_id, user_picks):
    """Create new picks for a user"""
    # 1. Delete existing picks
    UserPick.query.filter_by(user_id=user_id).delete()

    # 2. Insert new picks
    new_rows = [
        UserPick(
            user_id=user_id,
            game_id=pick["game_id"],
            predicted_winner_id=pick["team_id"]
        )
        for pick in user_picks
    ]
    
    db.session.bulk_save_objects(new_rows)
    db.session.commit()


def add_user_winner_pick(user_id, winner_name):
    """Add winner id to user profile"""
    # Find the team by name
    team = Team.query.filter_by(name=winner_name).first()

    # Update the user
    user = db.session.get(User, user_id)
    user.winner_id = team.team_id
    db.session.commit()


def add_user_final_score(user_id, score):
    """Add winner id to user profile"""
    user = db.session.get(User, user_id)
    user.final_score = score
    db.session.commit()


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


def reset_user_picks(user_id):
    """Clear all picks for a user"""
    UserPick.query.filter_by(user_id=user_id).delete()
    db.session.commit()


@bracket_bp.route("/reset-picks", methods=["POST"])
def reset_picks():
    """Reset user picks."""
    user_id = session["user_id"]
    reset_user_picks(user_id)
    return redirect(url_for("bracket.bracket"))
