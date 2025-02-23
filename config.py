import os

class Settings:
    BOOKS = ['draftkings', 'betmgm', 'fanduel', 'betrivers', 'pointsbetus']
    REGIONS = ['us']
    SPORTS = [
        # "americanfootball_ncaaf",
        # "baseball_ncaa",
        "basketball_nba",
        # "basketball_ncaa",
        # "basketball_wncaab",
        # "icehockey_nhl",
    ]
    MARKETS = [
        "h2h"
    ]
    API_KEY = os.environ['API_KEY']
    ODDS_FORMAT = 'decimal'
    DATE_FORMAT = 'iso'