import os

class Settings:
    BOOKS = ['draftkings', 'betmgm', 'fanduel', 'betrivers', 'pointsbetus']
    REGIONS = ['us']
    SPORTS = [
        # "americanfootball_ncaaf",
        # "baseball_ncaa",
        "basketball_nba",
        "basketball_ncaab",
        "basketball_wncaab",
        "icehockey_nhl",
        # "soccer_epl",
    ]
    MARKETS = [
        "h2h"
    ]
    API_KEY = os.environ['API_KEY']
    ODDS_FORMAT = 'decimal'
    DATE_FORMAT = 'iso'