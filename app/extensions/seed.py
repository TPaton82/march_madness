from app import db
from app.extensions.models import Team, Game, UserPick
from datetime import datetime

# Define teams per region — replace with actual names
EAST_TEAMS = [
    "Duke",
    "Alabama",
    "Wisconsin",
    "Arizona",
    "Oregon",
    "BYU",
    "Saint Mary's",
    "Miss. St.",
    "Baylor",
    "Vanderbilt",
    "VCU",
    "Liberty",
    "Akron",
    "Montana",
    "Robert Morris",
    "Mt St Mary's",
]

MIDWEST_TEAMS = [
    "Houston",
    "Tennessee",
    "Kentucky",
    "Purdue",
    "Clemson",
    "Illinois",
    "UCLA",
    "Gonzaga",
    "Georgia",
    "Utah St.",
    "Xavier",
    "McNeese",
    "High Point",
    "Troy",
    "Wofford",
    "SIUE",
]

SOUTH_TEAMS = [
    "Auburn",
    "Michigan St.",
    "Iowa St.",
    "Texas A&M",
    "Michigan",
    "Ole Miss",
    "Marquette",
    "Louisville",
    "Creighton",
    "New Mexico",
    "N. Carolina",
    "UC San Diego",
    "Yale",
    "Lipscomb",
    "Bryant",
    "Alabama St.",
]

WEST_TEAMS = [
    "Florida",
    "St. John's",
    "Texas Tech",
    "Maryland",
    "Memphis",
    "Missouri",
    "Kansas",
    "UConn",
    "Oklahoma",
    "Arkansas",
    "Drake",
    "Colo St.",
    "Grand Canyon",
    "UNCW",
    "Omaha",
    "Norfolk St.",
]

REGIONS = [("East", EAST_TEAMS), ("Midwest", MIDWEST_TEAMS), ("South", SOUTH_TEAMS), ("West", WEST_TEAMS)]

GAME_TIME = datetime(2025, 1, 1, 12, 0)

def clear_existing_tables():
    db.session.query(UserPick).delete()
    db.session.query(Game).delete()
    db.session.query(Team).delete()
    db.session.commit()

    print("Tables emptied")

def seed_teams():
    teams = []
    for region, names in REGIONS:
        for seed, name in enumerate(names, start=1):
            team = Team(name=name, seed=seed, region=region)
            db.session.add(team)
            teams.append(team)
    db.session.commit()
    print("Teams seeded.")
    return teams


def seed_round_1(teams):
    """Create round 1 games: 1v16, 2v15, etc. per region"""
    seed_to_order = {
        1: 1,
        8: 2,
        5: 3,
        4: 4,
        6: 5,
        3: 6,
        7: 7,
        2: 8
    }
    games = []
    for region, _ in REGIONS:
        region_teams = sorted([t for t in teams if t.region == region], key=lambda t: t.seed)
        for i in range(8):
            t1 = region_teams[i]
            t2 = region_teams[-(i + 1)]
            round_order = seed_to_order[t1.seed]
            game = Game(
                round=1,
                round_order=round_order,
                source_game_1=None,
                source_game_2=None,
                team_1_id=t1.team_id,
                team_2_id=t2.team_id,
                winner_id=None,
                region=region,
                game_time=GAME_TIME,
            )
            db.session.add(game)
            games.append(game)
    db.session.commit()
    print("Round 1 games seeded.")
    return games


def seed_future_rounds():
    """
    Automatically create placeholder games for rounds 2–6
    following the bracket logic from your SQL script.
    """
    for round_number in range(2, 7):
        if round_number == 2:
            prev_round = 1
        elif round_number == 3:
            prev_round = 2
        elif round_number == 4:
            prev_round = 3
        elif round_number == 5:
            prev_round = 4
        else:  # championship
            prev_round = 5

        # Fetch all games from previous round(s)
        prev_games = Game.query.filter_by(round=prev_round).order_by(Game.region, Game.round_order).all()
        regions = sorted(set(g.region for g in prev_games))

        if round_number == 5:
            regions = ["Final Four Left", "Final Four Right"]
        if round_number == 6:
            regions = ["Championship"]

        for region in regions:
            if round_number < 5:
                region_games = [g for g in prev_games if g.region == region]
            elif round_number == 5:
                if region == "Final Four Left":
                    region_games = [g for g in prev_games if g.region in ["South", "West"]] 
                if region == "Final Four Right":
                    region_games = [g for g in prev_games if g.region in ["Midwest", "East"]]
            else:
                region_games = prev_games

            # pair games sequentially: 1&2, 3&4, etc.
            for i in range(0, len(region_games), 2):
                    
                g1 = region_games[i]
                g2 = region_games[i + 1]

                new_game = Game(
                    round=round_number,
                    round_order=(i // 2) + 1,
                    source_game_1=g1.game_id,
                    source_game_2=g2.game_id,
                    team_1_id=None,
                    team_2_id=None,
                    winner_id=None,
                    region=region,
                    game_time=GAME_TIME,
                )
                db.session.add(new_game)
        db.session.commit()
        print(f"Round {round_number} games seeded.")
