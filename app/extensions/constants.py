from datetime import datetime, timezone


REGIONS = ["South", "Midwest", "West", "East", "Final Four Left", "Final Four Right", "Championship"]

ROUND_POINTS = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 6,
    6: 10
}

LOCK_TIME = datetime(2026, 3, 25, 0, 0, 0, tzinfo=timezone.utc)

NCAA_BASE_URL = "https://ncaa-api.henrygd.me"