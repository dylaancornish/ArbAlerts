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

class ArbOpportunity:
    def __init__(
        self,
        home_team,
        home_pct,
        home_price,
        away_team,
        away_pct,
        away_price,
        home_sportsbook,
        away_sportsbook,
        home_link,
        away_link,
        **kwargs
    ):
        self.home_team = home_team
        self.home_pct = home_pct
        self.home_price = home_price 
        self.away_team = away_team 
        self.away_pct = away_pct 
        self.away_price = away_price 
        self.home_sportsbook = home_sportsbook
        self.away_sportsbook = away_sportsbook

        self.home_link = home_link
        self.away_link = away_link

        self.calculate_metrics()

    def to_dict(self):
        import inspect
        
        return {
            k: v for k, v in inspect.getmembers(self)
            if not k.startswith('_') and not inspect.ismethod(v)
        }

    @classmethod
    def from_json(cls, json_str):
        return cls(**json.loads(json_str))
    
    def calculate_metrics(self):
        self.total_probability = self.home_pct + self.away_pct
        self.profit_pct = (1 - self.total_probability) / self.total_probability * 100

        total_stake = 100
        self.home_stake = round(self.home_pct * total_stake / self.total_probability, 2)
        self.away_stake = round(self.away_pct * total_stake / self.total_probability, 2)

        self.expected_return = total_stake * (1 + self.profit_pct/100)
        self.expected_profit = self.expected_return - total_stake

        self.home_stake_rounded = round(self.home_stake)
        self.away_stake_rounded = round(self.away_stake)
        self.rounded_total_stake = self.home_stake_rounded + self.away_stake_rounded

        self.home_outcome_rounded = self.home_stake_rounded * self.home_price
        self.away_outcome_rounded = self.away_stake_rounded * self.away_price
        
        self.min_profit_rounded = min(
            self.home_outcome_rounded - self.rounded_total_stake,
            self.away_outcome_rounded - self.rounded_total_stake
        )
        self.profit_pct_rounded = (self.min_profit_rounded / self.rounded_total_stake) * 100

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
        return cls(opportunities)

    def pretty_print_opportunities(self):
        if self.opportunities is None:
            return ""

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
                        away_sportsbook=away_sportsbook,
                        home_link='',
                        away_link=''
                    )
                    self.opportunities.append(arb_opportunity)
                    print(f"Bet {home_pct} of a unit on {game[home_team][1]}")
                    print(f"Bet {away_pct} of a unit on {game[away_team][1]}")
            