from collections import defaultdict
from app.extensions.db import db
from sqlalchemy.orm import aliased


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    winner_id = db.Column(db.Integer)
    final_score = db.Column(db.Integer, nullable=False)
    password_hash = db.Column(db.LargeBinary(32))
    salt = db.Column(db.LargeBinary(16))
    hash_algo = db.Column(db.String(10), nullable=False)
    iterations = db.Column(db.Integer, nullable=False)


class UserPick(db.Model):
    __tablename__ = "user_picks"

    pick_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    game_id = db.Column(db.Integer, nullable=False)
    predicted_winner_id = db.Column(db.Integer, nullable=False)


class Game(db.Model):
    __tablename__ = "games"

    game_id = db.Column(db.Integer, primary_key=True)
    round = db.Column(db.Integer, nullable=False)
    round_order = db.Column(db.Integer, nullable=False)
    source_game_1 = db.Column(db.Integer)
    source_game_2 = db.Column(db.Integer)
    team_1_id = db.Column(db.Integer)
    team_2_id = db.Column(db.Integer)
    winner_id = db.Column(db.Integer)
    region = db.Column(db.String(50), nullable=False)
    game_time = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "round": self.round,
            "round_order": self.round_order,
            "source_game_1": self.source_game_1,
            "source_game_2": self.source_game_2,
            "team_1_id": self.team_1_id,
            "team_2_id": self.team_2_id,
            "winner_id": self.winner_id,
            "region": self.region,
            "game_time": self.game_time,
        }


class Team(db.Model):
    __tablename__ = "teams"

    team_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    seed = db.Column(db.Integer, nullable=False)
    region = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "team_id": self.team_id,
            "name": self.name,
            "seed": self.seed,
            "region": self.region,
        }


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


def get_user_picks(user_id: int):
    """Getch user picks."""

    raw_picks = (
        db.session.query(UserPick.game_id, UserPick.predicted_winner_id, Team.seed)
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

    return {"team_id": team.team_id, "seed": team.seed, "name": team.name}


def get_user_final_score(user_id):
    """get user final score"""
    user = db.session.get(User, user_id)
    return {"value": user.final_score}


def get_team_names():
    """Fetch all team names"""
    raw_teams = Team.query.all()
    teams = {team.team_id: team.name for team in raw_teams}
    return teams
