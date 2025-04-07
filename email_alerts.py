import requests
import os
from datetime import datetime
from arb import ArbOpportunitySet

def send_mailgun_email(
    html_content: str, 
    to_email: str, 
    subject: str = "Arbitrage Alerts",
    mailgun_api_key: str = None,
    mailgun_domain: str = None
):
    if not mailgun_api_key:
        mailgun_api_key = os.getenv('MAILGUN_API_KEY')
    if not mailgun_domain:
        mailgun_domain = os.getenv('MAILGUN_DOMAIN')

    if not mailgun_api_key or not mailgun_domain:
        raise ValueError("Mailgun API Key and Domain must be provided")

    request_url = f'https://api.mailgun.net/v3/{mailgun_domain}/messages'

    request_data = {
        'from': f'Arbitrage Alerts <postmaster@sandbox80bd2a9b2b934bafa116fbbd1f276f16.mailgun.org>',
        'to': [to_email],
        'subject': subject,
        'html': html_content
    }

    response = requests.post(
        request_url,
        auth=('api', mailgun_api_key),
        data=request_data
    )

    if response.status_code == 200:
        print("Email sent successfully!")
        return response.json()
    else:
        print(f"Failed to send email. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def generate_html_email(opportunities_set: ArbOpportunitySet) -> str:
    """Generate HTML email content from arbitrage opportunities."""
    opportunities = opportunities_set.opportunities

    sorted_opps = sorted(opportunities, key=lambda x: x.profit_pct, reverse=True)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Arbitrage Alerts</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #2c3e50;
                color: white;
                padding: 15px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .alert-count {{
                font-size: 14px;
                color: #ecf0f1;
            }}
            .opportunity {{
                margin-bottom: 30px;
                border: 1px solid #ddd;
                border-radius: 5px;
                overflow: hidden;
            }}
            .opportunity-header {{
                background-color: #3498db;
                color: white;
                padding: 10px 15px;
                font-size: 18px;
                font-weight: bold;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .profit-badge {{
                background-color: #27ae60;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 16px;
            }}
            .matchup {{
                padding: 15px;
                background-color: #f8f9fa;
                border-bottom: 1px solid #ddd;
            }}
            .bet-details {{
                display: flex;
                justify-content: space-between;
                margin-top: 20px;
            }}
            .bet-card {{
                width: 48%;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 15px;
                background-color: white;
            }}
            .sportsbook {{
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }}
            .team {{
                font-size: 16px;
                margin-bottom: 10px;
            }}
            .odds {{
                font-size: 18px;
                font-weight: bold;
                color: #e74c3c;
            }}
            .stake-info {{
                margin-top: 10px;
                font-size: 14px;
            }}
            .profit-details {{
                padding: 15px;
                background-color: #e8f4fc;
            }}
            .profit-row {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
            }}
            .profit-label {{
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #7f8c8d;
                margin-top: 30px;
            }}
            .visit-btn {{
                display: inline-block;
                background-color: #3498db;
                color: white;
                padding: 5px 10px;
                text-decoration: none;
                border-radius: 3px;
                margin-top: 10px;
                font-size: 12px;
            }}
            .visit-btn:hover {{
                background-color: #2980b9;
            }}
            @media (max-width: 600px) {{
                .bet-details {{
                    flex-direction: column;
                }}
                .bet-card {{
                    width: 100%;
                    margin-bottom: 15px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Arbitrage Alerts</h1>
            <div class="alert-count">
                {len(opportunities)} opportunities found as of {datetime.now().strftime('%B %d, %Y %I:%M %p')}
            </div>
        </div>
    """

    for opp in sorted_opps:
        profit_pct_formatted = f"{opp.profit_pct:.2f}%"
        profit_rounded_formatted = f"{opp.profit_pct_rounded:.2f}%"
        
        html += f"""
        <div class="opportunity">
            <div class="opportunity-header">
                <span>{opp.home_team} vs {opp.away_team}</span>
                <span class="profit-badge">{profit_pct_formatted} profit</span>
            </div>
            
            <div class="matchup">
                <h3>Matchup Information</h3>
                <div class="bet-details">
                    <div class="bet-card">
                        <div class="sportsbook">{opp.home_sportsbook}</div>
                        <div class="team">{opp.home_team}</div>
                        <div class="odds">Odds: {opp.home_price}</div>
                        <div class="stake-info">
                            Recommended stake: ${opp.home_stake} (${opp.home_stake_rounded} rounded)
                        </div>
                        {f'<a href="{opp.home_link}" class="visit-btn" target="_blank">Visit Sportsbook</a>' if opp.home_link else ''}
                    </div>
                    
                    <div class="bet-card">
                        <div class="sportsbook">{opp.away_sportsbook}</div>
                        <div class="team">{opp.away_team}</div>
                        <div class="odds">Odds: {opp.away_price}</div>
                        <div class="stake-info">
                            Recommended stake: ${opp.away_stake} (${opp.away_stake_rounded} rounded)
                        </div>
                        {f'<a href="{opp.away_link}" class="visit-btn" target="_blank">Visit Sportsbook</a>' if opp.away_link else ''}
                    </div>
                </div>
            </div>
            
            <div class="profit-details">
                <h3>Profit Analysis</h3>
                
                <div class="profit-row">
                    <span class="profit-label">Total Investment:</span>
                    <span>${opp.home_stake + opp.away_stake:.2f} (exact) / ${opp.rounded_total_stake} (rounded)</span>
                </div>
                
                <div class="profit-row">
                    <span class="profit-label">Expected Return:</span>
                    <span>${opp.expected_return:.2f}</span>
                </div>
                
                <div class="profit-row">
                    <span class="profit-label">Expected Profit:</span>
                    <span>${opp.expected_profit:.2f} ({profit_pct_formatted})</span>
                </div>
                
                <div class="profit-row">
                    <span class="profit-label">Rounded Profit:</span>
                    <span>${opp.min_profit_rounded:.2f} ({profit_rounded_formatted})</span>
                </div>
            </div>
        </div>
        """
    
    html += """
        <div class="footer">
            <p>This is an educational project and not financial advice. No actual betting is recommended.</p>
            <p>Generated by Arbitrage Alert System</p>
        </div>
    </body>
    </html>
    """
    
    return html

def send_arbitrage_alerts(opportunities):
    html_email = generate_html_email(opportunities)

    try:
        send_mailgun_email(
            html_content=html_email, 
            to_email='dylaanc@gmail.com',
            subject=f'Arbitrage Opportunities {datetime.now()}'
        )
    except Exception as e:
        print(f"Error sending email: {e}")
