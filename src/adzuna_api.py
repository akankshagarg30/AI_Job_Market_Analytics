import os
import requests
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# Check that credentials exist
if not APP_ID or not APP_KEY:
    raise ValueError("Adzuna API credentials not found in .env")

# Adzuna India API
url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "results_per_page": 10,
    "what": "data analyst",
    "content-type": "application/json"
}

response = requests.get(url, params=params, timeout=30)

print("Status Code:", response.status_code)

if response.status_code == 200:
    data = response.json()

    print("Total matching jobs:", data.get("count"))
    print("Jobs returned:", len(data.get("results", [])))

    # Display available fields in the first job
    first_job = data.get("results", [])[0]

    print("\nAvailable fields:")
    for field in first_job.keys():
        print("-", field)
else:
    print("API request failed")
    print("Response:", response.text)