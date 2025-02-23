import requests
import os
from dotenv import load_dotenv
from config import Settings

class SportsbookAPI:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        max_retries: int = 3,
        retry_wait: int = 5
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self.session = requests.Session()

    def __enter__(
        self
    ):
        return self
    
    def __exit__(
        self, 
        exc_type, 
        exc_value, 
        traceback
    ) -> None:
        self.session.close()
    
    def get(
        self,
        endpoint: str,
        params: dict = {}
    ) -> dict:
        url = f"{self.base_url}/{endpoint}"

        if 'api_key' not in params.keys():
            params['api_key'] = self.api_key

        response = self.session.get(
            url,
            params=params
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Request failed with error {response.status_code}"}

    def _handle_rate_limit(
        self, 
        response: requests.Response,
        attempt: int
    ) -> bool:
        pass

class SportsbookOddsResponse:
    pass
