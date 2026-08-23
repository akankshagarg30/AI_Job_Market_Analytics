import json
import time
from datetime import datetime, timezone
from pathlib import Path

from api.adzuna_client import AdzunaClient


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# JOB ROLES TO COLLECT
# --------------------------------------------------

JOB_ROLES = [
    "data analyst",
    "data scientist",
    "data engineer",
    "business analyst",
    "BI analyst",
]


# --------------------------------------------------
# COLLECTION SETTINGS
# --------------------------------------------------

PAGES_PER_ROLE = 3
RESULTS_PER_PAGE = 50


# --------------------------------------------------
# COLLECT JOBS
# --------------------------------------------------

def collect_jobs():

    client = AdzunaClient()

    all_jobs = []

    collection_time = datetime.now(timezone.utc).isoformat()

    print("=" * 60)
    print("AI JOB MARKET DATA COLLECTION")
    print("=" * 60)

    for role in JOB_ROLES:

        print()
        print(f"Collecting role: {role}")

        for page in range(1, PAGES_PER_ROLE + 1):

            print(f"  Page {page}/{PAGES_PER_ROLE}")

            try:

                data = client.search_jobs(
                    country="in",
                    page=page,
                    keyword=role,
                    results_per_page=RESULTS_PER_PAGE,
                )

                jobs = data.get("results", [])

                print(f"  Jobs received: {len(jobs)}")

                for job in jobs:

                    job["_search_role"] = role
                    job["_collection_timestamp"] = collection_time

                all_jobs.extend(jobs)

                # Small delay between API requests
                time.sleep(1)

            except Exception as error:

                print(f"  ERROR collecting {role}, page {page}")
                print(f"  {error}")

    # --------------------------------------------------
    # SAVE RAW DATA
    # --------------------------------------------------

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S"
    )

    output_file = (
        RAW_DATA_DIR
        / f"job_market_raw_{timestamp}.json"
    )

    output_data = {
        "collection_timestamp": collection_time,
        "roles": JOB_ROLES,
        "pages_per_role": PAGES_PER_ROLE,
        "results_per_page": RESULTS_PER_PAGE,
        "total_jobs_collected": len(all_jobs),
        "results": all_jobs,
    }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output_data,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("COLLECTION COMPLETE")
    print("=" * 60)

    print(f"Total jobs collected: {len(all_jobs)}")
    print(f"Saved to: {output_file}")


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":
    collect_jobs()