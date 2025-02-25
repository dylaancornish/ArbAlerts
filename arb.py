from config import Settings
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

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

@dataclass
class ArbOpportunity:
    home_team: str
    home_pct: str
    home_price: str
    away_team: str
    away_pct: str
    away_price: str
    home_sportsbook: str
    away_sportsbook: str

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_json(cls, json_str):
        return cls(**json.loads(json_str))

class ArbOpportunitySet:
    def __init__(self, opportunities: Optional[list[ArbOpportunity]]=None):
        self.opportunities = []
        if opportunities is not None:
            print('opportunities is not none')
            self.opportunities = opportunities

    def add_opportunities(self, opportunities: list[ArbOpportunity]):
        self.opportunities.extend(opportunities)

    def to_json(self):
        return json.dumps([opportunity.to_dict() for opportunity in self.opportunities])

    def save_to_file(self, filename=f"arb_{datetime.now()}.json"):
        with open(filename, mode="w") as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, filename):
        with open(filename, mode="r") as f:
            opportunity_json = json.load(f)
        opportunities = [ArbOpportunity(**ao) for ao in opportunity_json]
        print(opportunities)
        return cls(opportunities)

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

                if (home_price == 0) or (away_price == 0):
                    continue

                home_pct = (1 / home_price)
                away_pct = (1 / away_price)
                arb_percent = home_pct + away_pct

                if arb_percent < 1.0:
                    home_sportsbook = game[home_team][1]
                    away_sportsbook = game[away_team][1]
                    arb_opportunity = ArbOpportunity(
                        home_team=home_team,
                        home_pct=home_pct,
                        home_price=home_price,
                        away_team=away_team,
                        away_pct=away_pct,
                        away_price=away_price,
                        home_sportsbook=home_sportsbook,
                        away_sportsbook=away_sportsbook
                    )
                    self.opportunities.append(arb_opportunity)
                    print(f"Bet {home_pct} of a unit on {game[home_team][1]}")
                    print(f"Bet {away_pct} of a unit on {game[away_team][1]}")
            