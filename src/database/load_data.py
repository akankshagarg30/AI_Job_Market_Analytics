import csv
from pathlib import Path

from connection import get_connection


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

JOBS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_clean.csv"
)

SKILLS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skills.csv"
)


# --------------------------------------------------
# LOAD JOB DATA
# --------------------------------------------------

def load_jobs(connection):

    print("Loading jobs_clean.csv...")

    cursor = connection.cursor()

    with open(
        JOBS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        jobs = list(reader)

    print(f"Jobs read from CSV: {len(jobs)}")

    # ----------------------------------------------
    # COMPANIES
    # ----------------------------------------------

    companies = sorted({
        job["company_name"]
        for job in jobs
        if job["company_name"]
    })

    for company in companies:

        cursor.execute(
            """
            INSERT INTO dim_company (company_name)
            VALUES (%s)
            ON CONFLICT (company_name)
            DO NOTHING;
            """,
            (company,)
        )

    print(
        f"Companies processed: {len(companies)}"
    )

    # ----------------------------------------------
    # LOCATIONS
    # ----------------------------------------------

    locations = sorted({
        job["location"]
        for job in jobs
        if job["location"]
    })

    for location in locations:

        cursor.execute(
            """
            INSERT INTO dim_location (location_name)
            VALUES (%s)
            ON CONFLICT (location_name)
            DO NOTHING;
            """,
            (location,)
        )

    print(
        f"Locations processed: {len(locations)}"
    )

    # ----------------------------------------------
    # CATEGORIES
    # ----------------------------------------------

    categories = sorted({
        job["category"]
        for job in jobs
        if job["category"]
    })

    for category in categories:

        cursor.execute(
            """
            INSERT INTO dim_category (category_name)
            VALUES (%s)
            ON CONFLICT (category_name)
            DO NOTHING;
            """,
            (category,)
        )

    print(
        f"Categories processed: {len(categories)}"
    )

    connection.commit()

    # ----------------------------------------------
    # LOAD FACT JOBS
    # ----------------------------------------------

    for job in jobs:

        cursor.execute(
            """
            SELECT company_id
            FROM dim_company
            WHERE company_name = %s;
            """,
            (job["company_name"],)
        )

        company_result = cursor.fetchone()

        company_id = (
            company_result[0]
            if company_result
            else None
        )

        cursor.execute(
            """
            SELECT location_id
            FROM dim_location
            WHERE location_name = %s;
            """,
            (job["location"],)
        )

        location_result = cursor.fetchone()

        location_id = (
            location_result[0]
            if location_result
            else None
        )

        cursor.execute(
            """
            SELECT category_id
            FROM dim_category
            WHERE category_name = %s;
            """,
            (job["category"],)
        )

        category_result = cursor.fetchone()

        category_id = (
            category_result[0]
            if category_result
            else None
        )

        salary_predicted = (
            job["salary_is_predicted"]
            if job["salary_is_predicted"]
            else None
        )

        if salary_predicted is not None:
            salary_predicted = (
                str(salary_predicted).lower()
                in ("1", "true", "yes")
            )

        cursor.execute(
            """
            INSERT INTO fact_jobs (
                job_id,
                title,
                company_id,
                location_id,
                category_id,
                description,
                created_at,
                contract_time,
                job_url,
                salary_is_predicted,
                adref,
                search_role,
                collection_timestamp
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s
            )
            ON CONFLICT (job_id)
            DO NOTHING;
            """,
            (
                job["job_id"],
                job["title"],
                company_id,
                location_id,
                category_id,
                job["description"],
                job["created_at"] or None,
                job["contract_time"] or None,
                job["job_url"] or None,
                salary_predicted,
                job["adref"] or None,
                job["search_role"] or None,
                job["collection_timestamp"] or None,
            )
        )

    connection.commit()

    print(
        f"Jobs loaded into fact_jobs: {len(jobs)}"
    )

    cursor.close()


# --------------------------------------------------
# LOAD SKILLS
# --------------------------------------------------

def load_skills(connection):

    print()
    print("Loading job_skills.csv...")

    cursor = connection.cursor()

    with open(
        SKILLS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        skill_rows = list(reader)

    skills = sorted({
        row["skill"]
        for row in skill_rows
        if row["skill"]
    })

    for skill in skills:

        cursor.execute(
            """
            INSERT INTO dim_skill (skill_name)
            VALUES (%s)
            ON CONFLICT (skill_name)
            DO NOTHING;
            """,
            (skill,)
        )

    connection.commit()

    print(
        f"Skills processed: {len(skills)}"
    )

    # ----------------------------------------------
    # JOB-SKILL RELATIONSHIPS
    # ----------------------------------------------

    relationships_loaded = 0

    for row in skill_rows:

        cursor.execute(
            """
            SELECT skill_id
            FROM dim_skill
            WHERE skill_name = %s;
            """,
            (row["skill"],)
        )

        skill_result = cursor.fetchone()

        if not skill_result:
            continue

        skill_id = skill_result[0]

        cursor.execute(
            """
            INSERT INTO job_skills (
                job_id,
                skill_id
            )
            VALUES (%s, %s)
            ON CONFLICT (job_id, skill_id)
            DO NOTHING;
            """,
            (
                row["job_id"],
                skill_id
            )
        )

        relationships_loaded += 1

    connection.commit()

    print(
        "Job-skill relationships processed:",
        relationships_loaded
    )

    cursor.close()


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("=" * 60)
    print("AI JOB MARKET DATABASE ETL")
    print("=" * 60)

    connection = None

    try:

        connection = get_connection()

        print("PostgreSQL connection successful.")
        print()

        load_jobs(connection)

        load_skills(connection)

        print()
        print("=" * 60)
        print("ETL COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as error:

        if connection:
            connection.rollback()

        print()
        print("ETL FAILED")
        print("Error:", error)

        raise

    finally:

        if connection:
            connection.close()

            print()
            print(
                "PostgreSQL connection closed."
            )


if __name__ == "__main__":
    main()