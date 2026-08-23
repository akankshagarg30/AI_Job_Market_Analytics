import json
from datetime import datetime, timezone
from pathlib import Path

from api.adzuna_client import AdzunaClient


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Raw data directory
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# Create directory if it doesn't exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_jobs():
    """Fetch jobs from Adzuna and save the raw API response."""

    client = AdzunaClient()

    data = client.search_jobs(
        country="in",
        page=1,
        keyword="data analyst",
        results_per_page=50,
    )

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S"
    )

    output_file = RAW_DATA_DIR / f"data_analyst_jobs_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    print("Data collection successful!")
    print("Total matching jobs:", data.get("count"))
    print("Jobs collected:", len(data.get("results", [])))
    print("Saved to:", output_file)


if __name__ == "__main__":
    fetch_jobs()