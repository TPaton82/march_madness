from datetime import datetime, timezone

from flask import Blueprint, render_template, request, session, url_for, redirect, jsonify
from app.extensions.models import (
    UserPick,
    User,
    Team,
    get_user_picks,
    get_user_winner_pick,
    get_user_final_score,
    get_team_names,
    get_game_winners
)
from app.extensions.utils import logged_in, get_team_logo, create_users_bracket_data
from app.extensions.db import db
from app.extensions.constants import LOCK_TIME

bracket_bp = Blueprint("bracket", __name__)


@bracket_bp.route("/bracket", methods=["GET"])
@logged_in
def bracket():
    """Create bracket page"""
    user_id = session["user_id"]
    user_picks = get_user_picks(user_id)
    winner = get_user_winner_pick(user_id)
    final_score = get_user_final_score(user_id)
    team_names = get_team_names()
    winners = get_game_winners()
    bracket_data = create_users_bracket_data(user_picks, team_names, winners)
    can_edit = datetime.now(timezone.utc) <= LOCK_TIME

    return render_template(
        "bracket.html",
        **bracket_data,
        winner=winner,
        final_score=final_score,
        user_picks=user_picks,
        get_team_logo=get_team_logo,
        can_edit=can_edit
    )


def create_user_picks(user_id, user_picks):
    """Create new picks for a user"""
    # 1. Delete existing picks
    UserPick.query.filter_by(user_id=user_id).delete()

    # 2. Insert new picks
    new_rows = [
        UserPick(user_id=user_id, game_id=pick["game_id"], predicted_winner_id=pick["team_id"]) for pick in user_picks
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

    if datetime.now(timezone.utc) >= LOCK_TIME:
        jsonify({"success": False, "message": "Picks are locked!"})

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
            add_user_final_score(user_id, final_score)
        except ValueError:
            pass


    return jsonify({"success": True, "message": "Picks saved!"})


def reset_user_picks(user_id):
    """Clear all picks for a user"""
    UserPick.query.filter_by(user_id=user_id).delete()
    db.session.commit()


@bracket_bp.route("/reset-picks", methods=["POST"])
def reset_picks():
    """Reset user picks."""

    if datetime.now(timezone.utc) >= LOCK_TIME:
        return {"error": "Picks are locked"}, 403
    
    user_id = session["user_id"]
    reset_user_picks(user_id)
    return redirect(url_for("bracket.bracket"))
