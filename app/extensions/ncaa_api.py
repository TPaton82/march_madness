import requests
import json
import pandas as pd
from app.extensions.constants import NCAA_BASE_URL


def get_current_scores():
    response = requests.get(NCAA_BASE_URL + "/scoreboard/basketball-men/d1")
    games = json.loads(response.text)["games"]

    game_data = {}

    for game in games:
        game_cfg = game["game"]

        game_data[game_cfg["gameID"]] = {
            "team_1_name": game_cfg["home"]["names"]["short"],
            "team_1_score": game_cfg["home"]["score"],
            "team_2_name": game_cfg["away"]["names"]["short"],
            "team_2_score": game_cfg["away"]["score"],
            "game_time": pd.to_datetime(game_cfg["startDate"] + " " + game_cfg["startTime"][:-3]).tz_localize("EST"),
            "game_period": game_cfg["currentPeriod"],
            "game_clock": game_cfg["contestClock"],
        }

    return game_data
