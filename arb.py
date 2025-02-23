from config import Settings

settings = Settings()

class Game:
    def __init__(
        self,
        game_dict: dict
    ):
        self.game_dict = game_dict
    
    def update_odds(self, best_odds, market, team, new_price, sportsbook):
        if market in best_odds and team in best_odds[market]:
            current_price, _ = best_odds[market][team]
            if new_price > current_price:
                best_odds[market][team] = (new_price, sportsbook)

    def find_best_opportunity(
        self,
        markets: list
    ):
        self.home_team = self.game_dict.get("home_team", None)
        self.away_team = self.game_dict.get("away_team", None)

        if (self.home_team is None) or (self.away_team is None):
            raise ValueError(f"Expected home and away team in game_dict. Actual keys are {list(self.game_dict.keys())}")
        
        best_odds = {
            m: {
                self.home_team: (0, ""),
                self.away_team: (0, "")
            } for m in markets
        }

        for odds in self.game_dict.get("bookmakers"):
            if odds["key"] in settings.BOOKS:
                for m in odds["markets"]:
                    if m["key"] not in markets:
                        continue
                    for outcome in m["outcomes"]:
                        self.update_odds(best_odds, m["key"], outcome["name"], outcome["price"], odds["key"])

        self.best_odds = best_odds

class ArbOpportunity:
    def __init__(
        self,
        home_team,
        home_pct,
        home_price,
        away_team,
        away_pct,
        away_price
    ):
        self.home_team = home_team
        self.home_pct = home_pct
        self.home_price = home_price
        self.away_team = away_team
        self.away_pct = away_pct
        self.away_price = away_price

class OddsParser:
    def __init__(
        self,
        raw_odds_data: list,
    ):
        self.raw_odds_data = raw_odds_data
        self.games = []
        self.opportunities = []

    def find_profitable_opportunities(
        self,
    ):
        for game_dict in self.raw_odds_data:
            g = Game(game_dict)
            g.find_best_opportunity(settings.MARKETS)
            self.games.append(g)
            best_odds = g.best_odds

            for game in best_odds.values():
                home_team = g.home_team
                away_team = g.away_team

                home_price = game[home_team][0]
                away_price = game[away_team][0]

                home_pct = (1 / home_price)
                away_pct = (1 / away_price)
                arb_percent = home_pct + away_pct
                print(f"{arb_percent}")
                if arb_percent < 1.0:
                    arb_opportunity = ArbOpportunity(
                        home_team, home_pct, home_price, away_team, away_pct, away_price
                    )
                    self.opportunities.append(arb_opportunity)
                    print(f"Bet {home_pct} of a unit on {game[home_team][1]}")
                    print(f"Bet {away_pct} of a unit on {game[away_team][1]}")
            