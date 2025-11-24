from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
from typing import List

# single shared MySQL extension instance
mysql = MySQL()


def create_user(name, password_hash, salt, hash_algo, iterations):
    """Create a new user."""
    cur = mysql.connection.cursor()

    cur.execute(
        "INSERT INTO users (name, password_hash, salt, hash_algo, iterations) VALUES (%s, %s, %s, %s, %s)",
        (name, password_hash, salt, hash_algo, iterations),
    )

    mysql.connection.commit()
    cur.close()


def get_user(name):
    """Fetch a user by name. Returns None if user does not exist."""
    cur = mysql.connection.cursor(DictCursor)

    cur.execute(f"SELECT user_id, name, password_hash, salt, hash_algo, iterations FROM users WHERE name = %s", (name,))
    row = cur.fetchone()

    if row is None:
        return None

    cur.close()

    return row


def get_all_users():
    """Fetch all users"""
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT user_id, name, winner_id, final_score FROM users")
    users = cur.fetchall()
    cur.close()
    return users


def get_all_games():
    """Fetch all users"""
    cur = mysql.connection.cursor(DictCursor)
    cur.execute(
        """
            SELECT 
                g.game_id, 
                g.round, 
                g.team_1_id, 
                t1.name as team_1_name, 
                g.team_2_id, 
                t2.name as team_2_name,
                g.winner_id 
            FROM games g
            LEFT JOIN teams t1 ON g.team_1_id = t1.team_id
            LEFT JOIN teams t2 ON g.team_2_id = t2.team_id
            ORDER BY g.round, g.game_id
        """
    )
    games = cur.fetchall()
    cur.close()
    return games


def get_completed_games():
    """Fetch all completed games"""
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT game_id, round, winner_id FROM games WHERE winner_id IS NOT NULL")
    raw_games = cur.fetchall()
    cur.close()

    completed_games = {game["game_id"]: game for game in raw_games}

    return completed_games


def get_team_name_from_id(team_id):
    """Fetch team name from the id"""
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("select name from teams where team_id = %s", (str(team_id),))
    team = cur.fetchone()

    if team:
        return team['name']

    return None


def get_team_names():
    """Fetch all team names"""
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("select team_id, name from teams")
    raw_teams = cur.fetchall()

    teams = {}
    for team in raw_teams:
        teams[team["team_id"]] = team["name"]

    cur.close()

    return teams


def get_bracket_data_for_region(region):
    """Fetch all bracket data"""
    cur = mysql.connection.cursor(DictCursor)

    cur.execute(
        """
            SELECT 
                g.game_id,
                g.round,
                g.source_game_1,
                g.source_game_2,
                g.team_1_id,
                g.team_2_id,
                t1.name AS team_1_name,
                t1.seed AS team_1_seed,
                t2.name AS team_2_name,
                t2.seed AS team_2_seed,
                g.winner_id,
                g.region,
                g.game_time
            FROM games g
                LEFT JOIN teams t1 ON g.team_1_id = t1.team_id
                LEFT JOIN teams t2 ON g.team_2_id = t2.team_id
            WHERE g.region = %s
            ORDER BY
				g.round,
                g.round_order;
        """,
        (region,),
    )

    bracket_data = cur.fetchall()

    # # Group games by round for easier rendering in the template
    rounds = {}
    for game in bracket_data:
        rounds.setdefault(game["round"], []).append(game)

    cur.close()

    return rounds


def get_upcoming_games_with_picks():
    """Fetch all upcoming games with user picks"""
    cur = mysql.connection.cursor(DictCursor)

    # ADD BACK IN 
    # WHERE g.game_time > NOW()

    cur.execute(
        """
            SELECT 
                g.game_id,
                g.round,
                g.game_time,
                g.team_1_id,
                t1.name AS team_1_name,
                t1.seed AS team_1_seed,

                g.team_2_id,
                t2.name AS team_2_name,
                t2.seed AS team_2_seed,

                up.user_id,
                u.name,
                up.predicted_winner_id

            FROM games g
                LEFT JOIN teams t1 ON g.team_1_id = t1.team_id
                LEFT JOIN teams t2 ON g.team_2_id = t2.team_id
                LEFT JOIN user_picks up ON g.game_id = up.game_id
                LEFT JOIN users u ON up.user_id = u.user_id
            WHERE t1.name IS NOT NULL
            AND t2.name IS NOT NULL
            ORDER BY g.game_time ASC;
        """
    )

    upcoming_games = cur.fetchall()
    return upcoming_games


def get_user_picks(user_id: int):
    """Getch user picks."""
    cur = mysql.connection.cursor(DictCursor)

    cur.execute(
        f"""
            SELECT 
                game_id, 
                predicted_winner_id,
                t.seed
            FROM user_picks up
				INNER JOIN teams t on up.predicted_winner_id = t.team_id
            WHERE user_id = %s
        """,
        str(user_id),
    )

    raw_picks = cur.fetchall()

    user_picks = {row["game_id"]: (row["predicted_winner_id"], row["seed"]) for row in raw_picks}

    cur.close()

    return user_picks


def create_user_picks(user_id, user_picks):
    """Create new picks for a user"""
    cur = mysql.connection.cursor()

    # First delete any existing picks
    query = "DELETE FROM user_picks WHERE user_id = %s"
    cur.execute(query, (str(user_id)))
    mysql.connection.commit()

    # Now insert the new picks
    query = "INSERT INTO user_picks (user_id, game_id, predicted_winner_id) VALUES (%s, %s, %s)"
    values = [(user_id, pick["game_id"], pick["team_id"]) for pick in user_picks]

    cur.executemany(query, values)

    mysql.connection.commit()
    cur.close()


def add_user_winner_pick(user_id, winner_name):
    """Add winner id to user profile"""
    cur = mysql.connection.cursor()

    cur.execute(f"SELECT team_id FROM teams WHERE name = %s", (winner_name,))
    team_id = cur.fetchone()

    # Now insert the new picks
    cur.execute(
        "UPDATE users SET winner_id = %s WHERE user_id = %s",
        (team_id, str(user_id)),
    )

    mysql.connection.commit()
    cur.close()

def update_game_winner(game_id, winner_id):
    """Update winner for a given game"""
    cur = mysql.connection.cursor()

    cur.execute(
        "UPDATE games SET winner_id = %s WHERE game_id = %s",
        (winner_id, game_id)
    )

    mysql.connection.commit()
    cur.close()


def add_user_final_score(user_id, score):
    """Add winner id to user profile"""
    cur = mysql.connection.cursor()

    cur.execute(
        "UPDATE users SET final_score = %s WHERE user_id = %s",
        (score, str(user_id)),
    )

    mysql.connection.commit()
    cur.close()


def get_user_winner_pick(user_id):
    """get user winner pick"""
    cur = mysql.connection.cursor(DictCursor)

    cur.execute(
        f"""
            SELECT 
                t.team_id, 
                t.seed, 
                t.name
            FROM users u
				INNER JOIN teams t on u.winner_id = t.team_id
            WHERE user_id = %s
        """,
        str(user_id),
    )

    winner_data = cur.fetchone()

    cur.close()

    return winner_data


def get_user_final_score(user_id):
    """get user final score"""
    cur = mysql.connection.cursor(DictCursor)

    cur.execute(
        f"""
            SELECT 
                u.final_score as value
            FROM users u
            WHERE user_id = %s
        """,
        str(user_id),
    )

    final_score = cur.fetchone()

    cur.close()

    return final_score


def reset_user_picks(user_id):
    """Clear all picks for a user"""
    cur = mysql.connection.cursor()

    # First delete any existing picks
    query = "DELETE FROM user_picks WHERE user_id = %s"
    cur.execute(query, (str(user_id)))
    mysql.connection.commit()

    cur.close()
