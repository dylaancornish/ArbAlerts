from sportsbook_api import SportsbookAPI
from arb import Game, OddsParser, ArbOpportunity, ArbOpportunitySet
from config import Settings
from email_alerts import send_arbitrage_alerts

from apscheduler.schedulers.background import BackgroundScheduler
import json
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_user_configs():
    """Load user configurations from JSON file"""
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading user configs: {e}")
        return {"default_user": {"email": "dylaanc@gmail.com", "schedule": "minutely"}}

def check_for_arbitrage(user_id, config):
    #TODO: pass user_id and config through to arb alert workflow
    """Run the arbitrage check for a specific user"""
    logger.info(f"Checking arbitrage for user {user_id} at {datetime.now()}")
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

    opportunity_set = ArbOpportunitySet()

    for odds_list in responses:
        op = OddsParser(odds_list)
        op.find_profitable_opportunities()
        
        if op.opportunities != []:
            opportunity_set.add_opportunities(op.opportunities)
    
    opportunity_set.save_to_file()
    # opportunity_set = ArbOpportunitySet.load_from_file('arb_2025-03-04 18:52:12.184957.json')
    send_arbitrage_alerts(opportunities=opportunity_set)

def setup_scheduler():
    """Set up and configure the scheduler based on user configurations"""
    scheduler = BackgroundScheduler()
    user_configs = load_user_configs()
    
    for user_id, config in user_configs.items():
        schedule_type = config.get("schedule", "hourly")

        if schedule_type == "hourly":
            scheduler.add_job(
                check_for_arbitrage, 
                'interval', 
                hours=1, 
                args=[user_id, config]
            )
        elif schedule_type == "daily":
            scheduler.add_job(
                check_for_arbitrage, 
                'cron', 
                hour=9,
                args=[user_id, config]
            )
        elif schedule_type == "minutely":
            scheduler.add_job(
                check_for_arbitrage,
                'interval',
                minutes=1,
                args=[user_id, config]
            )
    
    return scheduler

if __name__ == "__main__":
    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("Scheduler started. Press Ctrl+C to exit")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shut down")
    