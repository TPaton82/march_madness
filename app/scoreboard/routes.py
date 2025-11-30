from collections import defaultdict
from flask import Blueprint, render_template, session
from sqlalchemy.orm import aliased
from sqlalchemy import func

from app.extensions.models import (
    Game,
    UserPick,
    User,
    Team,
    get_user_picks,
    get_user_winner_pick,
    get_user_final_score,
    get_team_names
)
from app.extensions.utils import logged_in, get_team_logo, create_users_bracket_data
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


def get_user_id_from_name(user_name):
    """Fetch team name from the id"""
    user = User.query.filter(func.lower(User.name) == user_name.lower()).first()
    return user.user_id if user else None


def get_user_picks(user_id: int):
    """Getch user picks."""

    raw_picks = (
        db.session.query(UserPick.game_id, UserPick.predicted_winner_id, Team.seed)
        .join(Team, UserPick.predicted_winner_id == Team.team_id)
        .filter(UserPick.user_id == user_id)
    ).all()

    user_picks = {pick.game_id: (pick.predicted_winner_id, pick.seed) for pick in raw_picks}

    return user_picks


def get_completed_games():
    """Fetch all completed games"""
    raw_games = Game.query.filter(Game.winner_id.isnot(None)).all()

    completed_games = {game.game_id: game.to_dict() for game in raw_games}

    return completed_games


def get_all_games():
    """Fetch all games"""
    team_1 = aliased(Team)
    team_2 = aliased(Team)

    games = (
        db.session.query(
            Game.game_id,
            Game.round,
            Game.source_game_1,
            Game.source_game_2,
            Game.team_1_id,
            team_1.name.label("team_1_name"),
            Game.team_2_id,
            team_2.name.label("team_2_name"),
            Game.winner_id,
        )
        .outerjoin(team_1, Game.team_1_id == team_1.team_id)
        .outerjoin(team_2, Game.team_2_id == team_2.team_id)
        .order_by(Game.round, Game.game_id)
        .all()
    )

    return games


def build_team_alive_set(games):
    """Build set of teams that are still alive"""
    alive = set()

    for game in games:
        # Add any team that appears in actual data as a still-valid winning path
        for team in (game.team_1_id, game.team_2_id):
            if team:
                alive.add(team)

    # Remove eliminated teams
    for game in games:
        # if the game has a real winner, the losing team is eliminated
        if game.winner_id:
            loser = game.team_1_id if game.team_2_id == game.winner_id else game.team_2_id
            alive.discard(loser)

    return alive


def can_team_reach_game(team_id, game_id, games_by_id):
    """Check whether a given team can reach a given game"""
    game = games_by_id[game_id]

    # Base case: first round
    if not game.source_game_1 and not game.source_game_2:
        return True

    for source_game in [game.source_game_1, game.source_game_2]:
        if source_game is None:
            continue

        parent_game = games_by_id[source_game]

        # Parent game resolved already
        if parent_game.winner_id:
            if parent_game.winner_id != team_id:
                return False
        else:
            # Parent unresolved → still possible
            continue

    return True


def calculate_maximum_points(user_picks, all_games):
    games_by_id = {g.game_id: g for g in all_games}
    alive_teams = build_team_alive_set(all_games)

    maximum_points = 0

    for g in all_games:
        predicted_team, predicted_seed = user_picks.get(g.game_id, (None, None))

        if not predicted_team:
            continue

        # Already resolved → max points impossible here
        if g.winner_id is not None:
            continue

        # Team already eliminated
        if predicted_team not in alive_teams:
            continue

        # Can this team still *logically* reach this game?
        if can_team_reach_game(predicted_team, g.game_id, games_by_id):
            maximum_points += ROUND_POINTS[g.round] + predicted_seed

    return maximum_points


def calculate_scoreboard():
    """Calculate the current scoreboard"""
    users = get_all_users()

    picks_by_user = {}
    for user in users:
        user_picks = get_user_picks(user.user_id)
        picks_by_user[user.name] = {
            "user_picks": user_picks,
            "winner_data": {
                "predicted_champion_name": get_team_name_from_id(user.winner_id),
                "predicted_final_score": user.final_score,
            },
        }

    completed_games = get_completed_games()

    scoreboard = []
    for user_name, user_data in picks_by_user.items():
        user_picks = user_data["user_picks"]

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
        maximum_points = calculate_maximum_points(user_picks, all_games)

        scoreboard.append(
            {
                "username": user_name.title(),
                "current_points": current_points,
                "max_points": maximum_points,
                "correct_picks": total_correct,
                "round_scores": user_round_scores,
                **user_data["winner_data"],
            }
        )

    return sorted(scoreboard, key=lambda user: user["current_points"], reverse=True)


@scoreboard_bp.route("/scoreboard", methods=["GET"])
@logged_in
def scoreboard():
    """Render the scoreboard"""
    scoreboard = calculate_scoreboard()

    return render_template("scoreboard.html", scoreboard=scoreboard, get_team_logo=get_team_logo)


@scoreboard_bp.route("/picks/<name>")
@logged_in
def user_draft_page(name):
    # do DB lookup using name
    """Create bracket page for given user"""
    current_user_name = session["user_name"]
    user_id = get_user_id_from_name(name)
    user_picks = get_user_picks(user_id)
    winner = get_user_winner_pick(user_id)
    final_score = get_user_final_score(user_id)
    team_names = get_team_names()
    bracket_data = create_users_bracket_data(user_picks, team_names)

    can_edit = current_user_name.lower() == name.lower()

    return render_template(
        "bracket.html",
        **bracket_data,
        winner=winner,
        final_score=final_score,
        user_picks=user_picks,
        get_team_logo=get_team_logo,
        can_edit=can_edit
    )
