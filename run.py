from sportsbook_api import SportsbookAPI
from arb import Game, OddsParser, ArbOpportunity, ArbOpportunitySet
from config import Settings
from email_alerts import send_arbitrage_alerts

if __name__ == "__main__":
    settings = Settings()
    responses = []

    with SportsbookAPI(
        base_url = 'https://api.the-odds-api.com/v4',
        api_key = settings.API_KEY,
    ) as api:
        for sport in settings.SPORTS:
            params={
                'api_key': settings.API_KEY,
                'regions': ','.join(settings.REGIONS).strip(),
                'markets': ','.join(settings.MARKETS).strip(),
                'oddsFormat': settings.ODDS_FORMAT,
                'dateFormat': settings.DATE_FORMAT,
                'includeLinks': settings.INCLUDE_LINKS,
            }
            response = api.get(
                endpoint=f"sports/{sport}/odds",
                params=params
            )
            responses.append(response)
            print(response)

    opportunity_set = ArbOpportunitySet()

    for odds_list in responses:
        op = OddsParser(odds_list)
        op.find_profitable_opportunities()
        
        if op.opportunities != []:
            opportunity_set.add_opportunities(op.opportunities)
    
    opportunity_set.save_to_file()
    opportunity_set = ArbOpportunitySet.load_from_file('arb_2025-03-04 18:52:12.184957.json')
    send_arbitrage_alerts(opportunities=opportunity_set)
    