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
    results_per_page=20
):
    """
    Fetch jobs from Adzuna API.

    Returns:
        dict: Complete Adzuna API response.
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

    return response.json()


# =========================================================
# CONNECT TO SUPABASE POSTGRESQL
# =========================================================

def get_db_connection():
    """
    Create a secure SSL connection to Supabase PostgreSQL.
    """

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
    """
    Insert jobs into PostgreSQL.

    Existing jobs are skipped using job_id.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    inserted = 0
    skipped = 0

    for job in jobs:

        # -------------------------------------------------
        # SAFETY CHECK
        # -------------------------------------------------

        if not isinstance(job, dict):
            print(
                f"Skipping invalid job record: {job}"
            )
            skipped += 1
            continue

        # -------------------------------------------------
        # BASIC JOB INFORMATION
        # -------------------------------------------------

        job_id = job.get("id")

        if not job_id:
            skipped += 1
            continue

        title = job.get("title")

        # -------------------------------------------------
        # COMPANY
        # -------------------------------------------------

        company_data = job.get("company") or {}

        if isinstance(company_data, dict):
            company = company_data.get("display_name")
        else:
            company = str(company_data)

        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        location_data = job.get("location") or {}

        if isinstance(location_data, dict):
            location_name = location_data.get(
                "display_name"
            )
        else:
            location_name = str(location_data)

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        category_data = job.get("category") or {}

        if isinstance(category_data, dict):
            category = category_data.get("label")
        else:
            category = str(category_data)

        # -------------------------------------------------
        # OTHER FIELDS
        # -------------------------------------------------

        description = job.get("description")

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
        # INSERT INTO DATABASE
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
                location_name,
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
# MAIN ETL PROCESS
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("JOBLENS AI — INDIA JOB MARKET ETL")
    print("=" * 60)

    # -----------------------------------------------------
    # JOB SEARCH CONFIGURATION
    # -----------------------------------------------------

    searches = [

        # DATA ANALYST
        ("data analyst", "Bangalore"),
        ("data analyst", "Mumbai"),
        ("data analyst", "Delhi"),
        ("data analyst", "Hyderabad"),
        ("data analyst", "Pune"),

        # DATA SCIENTIST
        ("data scientist", "Bangalore"),
        ("data scientist", "Mumbai"),
        ("data scientist", "Delhi"),
        ("data scientist", "Hyderabad"),
        ("data scientist", "Pune"),

        # DATA ENGINEER
        ("data engineer", "Bangalore"),
        ("data engineer", "Mumbai"),
        ("data engineer", "Delhi"),
        ("data engineer", "Hyderabad"),
        ("data engineer", "Pune"),

        # BUSINESS ANALYST
        ("business analyst", "Bangalore"),
        ("business analyst", "Mumbai"),
        ("business analyst", "Delhi"),
        ("business analyst", "Hyderabad"),
        ("business analyst", "Pune"),

        # POWER BI
        ("power bi", "Bangalore"),
        ("power bi", "Mumbai"),
        ("power bi", "Delhi"),
        ("power bi", "Hyderabad"),
        ("power bi", "Pune"),
    ]

    total_received = 0
    total_inserted = 0
    total_skipped = 0

    # -----------------------------------------------------
    # RUN EACH SEARCH
    # -----------------------------------------------------

    for keyword, location in searches:

        print("\n" + "-" * 60)

        print(
            f"Searching: {keyword.title()} "
            f"in {location}"
        )

        try:

            # ---------------------------------------------
            # FETCH
            # ---------------------------------------------

            data = fetch_jobs(
                keyword=keyword,
                location=location,
                page=1,
                results_per_page=20
            )

            jobs = data.get(
                "results",
                []
            )

            print(
                f"Jobs received: {len(jobs)}"
            )

            total_received += len(jobs)

            # ---------------------------------------------
            # LOAD
            # ---------------------------------------------

            if jobs:

                inserted, skipped = insert_jobs(
                    jobs
                )

                print(
                    f"Inserted: {inserted} | "
                    f"Skipped: {skipped}"
                )

                total_inserted += inserted
                total_skipped += skipped

        except Exception as error:

            print(
                f"ERROR while processing "
                f"{keyword} - {location}:"
            )

            print(error)

    # -----------------------------------------------------
    # FINAL SUMMARY
    # -----------------------------------------------------

    print("\n")

    print("=" * 60)
    print("ETL COMPLETED")
    print("=" * 60)

    print(
        f"Total jobs received : "
        f"{total_received}"
    )

    print(
        f"New jobs inserted   : "
        f"{total_inserted}"
    )

    print(
        f"Duplicate jobs      : "
        f"{total_skipped}"
    )

    print("=" * 60)