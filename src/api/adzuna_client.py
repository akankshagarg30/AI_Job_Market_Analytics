import os
import requests
from dotenv import load_dotenv


class AdzunaClient:
    """Client for interacting with the Adzuna Jobs API."""

    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(self):
        load_dotenv()

        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")

        if not self.app_id or not self.app_key:
            raise ValueError(
                "ADZUNA_APP_ID and ADZUNA_APP_KEY must be set in .env"
            )

    def search_jobs(
        self,
        country="in",
        page=1,
        keyword="data analyst",
        results_per_page=10,
    ):
        """Search jobs from Adzuna."""

        url = f"{self.BASE_URL}/{country}/search/{page}"

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": results_per_page,
            "what": keyword,
            "content-type": "application/json",
        }

        response = requests.get(
            url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()