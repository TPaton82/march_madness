from collections import defaultdict
from flask import Blueprint, render_template
from sqlalchemy.orm import aliased

from app.extensions.models import Game, Team, User, UserPick
from app.extensions.db import db
from app.extensions.utils import logged_in, get_team_logo
from app.extensions.constants import ROUND_POINTS


scoreboard_bp = Blueprint("scoreboard", __name__)


def get_team_name_from_id(team_id):
    """Fetch team name from the id"""
    team = Team.query.filter_by(team_id=team_id).first()
    return team.name if team else None


def get_all_users():
    """Fetch all users"""
    return User.query.all()


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


def get_completed_games():
    """Fetch all completed games"""
    raw_games = Game.query.filter(Game.winner_id.isnot(None)).all()

    completed_games = {
        game.game_id: game.to_dict()
        for game in raw_games
    }

    return completed_games


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


def calculate_scoreboard():
    """Calculate the current scoreboard"""
    users = get_all_users()

    picks_by_user = {}
    for user in users:
        user_picks = get_user_picks(user.user_id)
        picks_by_user[user.name] = user_picks

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
            game_id = game.game_id
            round = game.round
            predicted_pick, predicted_seed = user_picks.get(game_id, (None, None))

            # Already scored
            if game.winner_id is not None:
                continue

            # If predicted team still alive, add points
            if predicted_pick and predicted_pick in [game.team_1_id, game.team_2_id]:
                maximum_points += ROUND_POINTS[round] + predicted_seed

        predicted_champion = get_team_name_from_id(user.winner_id)

        scoreboard.append(
            {
                "username": user_name.title(),
                "current_points": current_points,
                "max_points": current_points + maximum_points,
                "correct_picks": total_correct,
                "round_scores": user_round_scores,
                "predicted_champion_name": predicted_champion,
                "predicted_final_score": user.final_score,
            }
        )

    return scoreboard


@scoreboard_bp.route("/scoreboard", methods=["GET"])
@logged_in
def scoreboard():
    """Render the scoreboard"""
    scoreboard = calculate_scoreboard()

    return render_template("scoreboard.html", scoreboard=scoreboard, get_team_logo=get_team_logo)
