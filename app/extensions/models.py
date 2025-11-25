from app.extensions.db import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    winner_id = db.Column(db.Integer)
    final_score = db.Column(db.Integer)
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