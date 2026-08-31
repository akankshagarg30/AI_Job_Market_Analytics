import os
import requests
import psycopg2
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
ADZUNA_COUNTRY = os.getenv("ADZUNA_COUNTRY", "in")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# =========================================================
# VALIDATE ENVIRONMENT VARIABLES
# =========================================================

required_variables = {
    "ADZUNA_APP_ID": ADZUNA_APP_ID,
    "ADZUNA_APP_KEY": ADZUNA_APP_KEY,
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
}

missing_variables = [
    name
    for name, value in required_variables.items()
    if not value
]

if missing_variables:
    raise ValueError(
        "Missing environment variables: "
        + ", ".join(missing_variables)
    )


# =========================================================
# FETCH JOBS FROM ADZUNA
# =========================================================

def fetch_jobs(
    keyword="data analyst",
    location=None,
    page=1,
    results_per_page=10
):
    """
    Fetch jobs from Adzuna API.
    Returns a list of job dictionaries.
    """

    url = (
        f"https://api.adzuna.com/v1/api/jobs/"
        f"{ADZUNA_COUNTRY}/search/{page}"
    )

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": keyword,
        "content-type": "application/json"
    }

    if location:
        params["where"] = location

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data.get("results", [])


# =========================================================
# CONNECT TO SUPABASE POSTGRESQL
# =========================================================

def get_db_connection():

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require"
    )


# =========================================================
# INSERT JOBS INTO DATABASE
# =========================================================

def insert_jobs(jobs):

    connection = get_db_connection()
    cursor = connection.cursor()

    inserted = 0
    skipped = 0

    for job in jobs:

        # Make sure we have a job dictionary
        if not isinstance(job, dict):
            print(
                "⚠️ Invalid job format. Skipping."
            )
            skipped += 1
            continue

        job_id = job.get("id")

        if not job_id:
            skipped += 1
            continue

        title = job.get("title")

        company_data = job.get("company") or {}

        if isinstance(company_data, dict):
            company = company_data.get(
                "display_name"
            )
        else:
            company = str(company_data)

        location_data = job.get("location") or {}

        if isinstance(location_data, dict):
            location = location_data.get(
                "display_name"
            )
        else:
            location = str(location_data)

        description = job.get("description")

        category_data = job.get("category") or {}

        if isinstance(category_data, dict):
            category = category_data.get(
                "label"
            )
        else:
            category = str(category_data)

        contract_type = job.get(
            "contract_type"
        )

        contract_time = job.get(
            "contract_time"
        )

        salary_min = job.get(
            "salary_min"
        )

        salary_max = job.get(
            "salary_max"
        )

        salary_is_predicted = job.get(
            "salary_is_predicted"
        )

        created_date = job.get(
            "created"
        )

        redirect_url = job.get(
            "redirect_url"
        )

        source = "Adzuna"

        # -------------------------------------------------
        # INSERT JOB
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO jobs (
                job_id,
                title,
                company,
                location,
                description,
                category,
                contract_type,
                contract_time,
                salary_min,
                salary_max,
                salary_is_predicted,
                created_date,
                redirect_url,
                source,
                fetched_at
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT (job_id)
            DO NOTHING
            """,
            (
                job_id,
                title,
                company,
                location,
                description,
                category,
                contract_type,
                contract_time,
                salary_min,
                salary_max,
                salary_is_predicted,
                created_date,
                redirect_url,
                source
            )
        )

        if cursor.rowcount == 1:
            inserted += 1
        else:
            skipped += 1

    connection.commit()

    cursor.close()
    connection.close()

    return inserted, skipped


# =========================================================
# MAIN ETL PIPELINE
# =========================================================

if __name__ == "__main__":

    print()
    print("================================")
    print("JOBLENS AI - DAILY ETL PIPELINE")
    print("================================")

    # -----------------------------------------------------
    # STEP 1 — FETCH
    # -----------------------------------------------------

    print()
    print("Step 1: Fetching jobs from Adzuna...")
    print()

    try:

        jobs = fetch_jobs(
            keyword="data analyst",
            page=1,
            results_per_page=10
        )

        print(
            f"Jobs received: {len(jobs)}"
        )

    except Exception as error:

        print(
            f"❌ Failed to fetch jobs: {error}"
        )

        raise SystemExit(1)

    # -----------------------------------------------------
    # STEP 2 — DATABASE LOAD
    # -----------------------------------------------------

    print()
    print("Step 2: Loading jobs into Supabase PostgreSQL...")
    print()

    try:

        inserted, skipped = insert_jobs(jobs)

        print("==============================")
        print("DATABASE LOAD COMPLETED")
        print("==============================")

        print(
            f"Jobs received : {len(jobs)}"
        )

        print(
            f"Jobs inserted : {inserted}"
        )

        print(
            f"Jobs skipped  : {skipped}"
        )

        print("==============================")

    except Exception as error:

        print(
            f"❌ Database loading failed: {error}"
        )

        raise SystemExit(1)

    print()
    print("✅ ETL pipeline completed successfully!")