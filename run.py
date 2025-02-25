from sportsbook_api import SportsbookAPI
from arb import Game, OddsParser, ArbOpportunity, ArbOpportunitySet
from config import Settings

if __name__ == "__main__":
    settings = Settings()
    responses = []

    # with SportsbookAPI(
    #     base_url = 'https://api.the-odds-api.com/v4',
    #     api_key = settings.API_KEY,
    # ) as api:
    #     for sport in settings.SPORTS:
    #         params={
    #             'api_key': settings.API_KEY,
    #             'regions': ','.join(settings.REGIONS).strip(),
    #             'markets': ','.join(settings.MARKETS).strip(),
    #             'oddsFormat': settings.ODDS_FORMAT,
    #             'dateFormat': settings.DATE_FORMAT,
    #         }
    #         response = api.get(
    #             endpoint=f"sports/{sport}/odds",
    #             params=params
    #         )
    #         responses.append(response)

    # opportunity_set = ArbOpportunitySet()

    # for odds_list in responses:
    #     op = OddsParser(odds_list)
    #     op.find_profitable_opportunities()
        
    #     if op.opportunities != []:
    #         opportunity_set.add_opportunities(op.opportunities)
    
    # opportunity_set.save_to_file()
    opportunity_set = ArbOpportunitySet.load_from_file('arb_2025-02-24 20:20:08.359876.json')
    