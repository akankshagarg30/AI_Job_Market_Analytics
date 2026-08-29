import csv
import json
from pathlib import Path
from datetime import datetime


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# FIND LATEST RAW FILE
# --------------------------------------------------

raw_files = sorted(
    RAW_DATA_DIR.glob("job_market_raw_*.json")
)

if not raw_files:
    raise FileNotFoundError(
        "No job market raw JSON file found."
    )

latest_raw_file = raw_files[-1]

print("Using raw file:")
print(latest_raw_file)


# --------------------------------------------------
# LOAD RAW JSON
# --------------------------------------------------

with open(
    latest_raw_file,
    "r",
    encoding="utf-8"
) as file:

    raw_data = json.load(file)


jobs = raw_data.get("results", [])

print()
print("Raw jobs loaded:", len(jobs))


# --------------------------------------------------
# OUTPUT COLUMNS
# --------------------------------------------------

columns = [
    "job_id",
    "title",
    "company_name",
    "location",
    "category",
    "description",
    "created_at",
    "contract_time",
    "job_url",
    "salary_is_predicted",
    "adref",
    "search_role",
    "collection_timestamp",
]


# --------------------------------------------------
# TRANSFORM + DEDUPLICATE
# --------------------------------------------------

clean_jobs = []

seen_job_ids = set()

duplicates_removed = 0


for job in jobs:

    job_id = str(job.get("id", "")).strip()

    # Skip duplicate jobs
    if job_id in seen_job_ids:
        duplicates_removed += 1
        continue

    seen_job_ids.add(job_id)

    company = job.get("company") or {}
    location = job.get("location") or {}
    category = job.get("category") or {}

    clean_job = {
        "job_id": job_id,

        "title": str(
            job.get("title") or ""
        ).strip(),

        "company_name": str(
            company.get("display_name") or ""
        ).strip(),

        "location": str(
            location.get("display_name") or ""
        ).strip(),

        "category": str(
            category.get("label") or ""
        ).strip(),

        "description": str(
            job.get("description") or ""
        ).strip(),

        "created_at": job.get("created"),

        "contract_time": str(
            job.get("contract_time") or ""
        ).strip(),

        "job_url": str(
            job.get("redirect_url") or ""
        ).strip(),

        "salary_is_predicted": job.get(
            "salary_is_predicted"
        ),

        "adref": str(
            job.get("adref") or ""
        ).strip(),

        "search_role": str(
            job.get("_search_role") or ""
        ).strip(),

        "collection_timestamp": job.get(
            "_collection_timestamp"
        ),
    }

    clean_jobs.append(clean_job)


# --------------------------------------------------
# SAVE CLEAN CSV
# --------------------------------------------------

output_file = (
    PROCESSED_DATA_DIR
    / "jobs_clean.csv"
)


with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=columns
    )

    writer.writeheader()

    writer.writerows(clean_jobs)


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print()
print("=" * 60)
print("TRANSFORMATION COMPLETE")
print("=" * 60)

print("Raw records:", len(jobs))
print(
    "Duplicates removed:",
    duplicates_removed
)

print(
    "Clean records:",
    len(clean_jobs)
)

print()
print("Columns:")

for column in columns:
    print("-", column)

print()
print("Saved to:")
print(output_file)