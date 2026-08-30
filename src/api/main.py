from fastapi import FastAPI, HTTPException
from src.database.connection import get_connection
from pydantic import BaseModel


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="AI Job Market Analytics API",
    description="REST API for the AI Job Market Analytics Platform",
    version="1.0.0"
)


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class CandidateRequest(BaseModel):
    skills: list[str]
    role: str | None = None
    location: str | None = None
    experience: str | None = None
    salary: str | None = None


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "AI Job Market Analytics API is running"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# --------------------------------------------------
# GET JOBS
# --------------------------------------------------

@app.get("/jobs")
def get_jobs(
    role: str | None = None,
    location: str | None = None
):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                f.job_id,
                f.title,
                c.company_name,
                l.location_name,
                f.description,
                f.contract_time,
                f.job_url
            FROM public.fact_jobs f

            LEFT JOIN public.dim_company c
                ON f.company_id = c.company_id

            LEFT JOIN public.dim_location l
                ON f.location_id = l.location_id

            WHERE 1=1
        """

        params = []

        # --------------------------------------------------
        # ROLE FILTER
        # --------------------------------------------------

        if role and role.lower() != "all roles":

            query += """
                AND f.title ILIKE %s
            """

            params.append(
                f"%{role}%"
            )

        # --------------------------------------------------
        # LOCATION FILTER
        # --------------------------------------------------

        if location and location.lower() != "all locations":

            query += """
                AND l.location_name ILIKE %s
            """

            params.append(
                f"%{location}%"
            )

        # --------------------------------------------------
        # ORDER
        # --------------------------------------------------

        query += """
            ORDER BY f.created_at DESC
            LIMIT 100
        """

        cursor.execute(
            query,
            params
        )

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        jobs = [
            dict(zip(columns, row))
            for row in rows
        ]

        return {
            "count": len(jobs),
            "jobs": jobs
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# GET SINGLE JOB
# --------------------------------------------------

@app.get("/jobs/{job_id}")
def get_job(job_id: str):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM public.fact_jobs
            WHERE job_id = %s
            """,
            (job_id,)
        )

        row = cursor.fetchone()

        if row is None:

            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        columns = [
            description[0]
            for description in cursor.description
        ]

        job = dict(
            zip(columns, row)
        )

        return job

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# GET JOB SKILLS
# --------------------------------------------------

@app.get("/jobs/{job_id}/skills")
def get_job_skills(job_id: str):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT ds.skill_name
            FROM public.job_skills js

            JOIN public.dim_skill ds
                ON js.skill_id = ds.skill_id

            WHERE js.job_id = %s

            ORDER BY ds.skill_name
            """,
            (job_id,)
        )

        rows = cursor.fetchall()

        return {
            "job_id": job_id,
            "skills": [
                row[0]
                for row in rows
            ]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# GET ALL SKILLS
# --------------------------------------------------

@app.get("/skills")
def get_skills():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                s.skill_id,
                s.skill_name,
                COUNT(DISTINCT js.job_id) AS job_count

            FROM public.dim_skill s

            LEFT JOIN public.job_skills js
                ON s.skill_id = js.skill_id

            GROUP BY
                s.skill_id,
                s.skill_name

            ORDER BY
                job_count DESC,
                s.skill_name
            """
        )

        rows = cursor.fetchall()

        skills = [
            {
                "skill_id": row[0],
                "skill": row[1],
                "job_count": row[2]
            }
            for row in rows
        ]

        return {
            "count": len(skills),
            "skills": skills
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# GET TOP SKILLS
# --------------------------------------------------

@app.get("/skills/top")
def get_top_skills():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                s.skill_name,
                COUNT(DISTINCT js.job_id) AS job_count

            FROM public.dim_skill s

            INNER JOIN public.job_skills js
                ON s.skill_id = js.skill_id

            GROUP BY
                s.skill_name

            ORDER BY
                job_count DESC

            LIMIT 10
            """
        )

        rows = cursor.fetchall()

        skills = [
            {
                "skill": row[0],
                "job_count": row[1]
            }
            for row in rows
        ]

        return {
            "skills": skills
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# GET COMPANIES
# --------------------------------------------------

@app.get("/companies")
def get_companies():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                c.company_id,
                c.company_name,
                COUNT(f.job_id) AS job_count

            FROM public.dim_company c

            LEFT JOIN public.fact_jobs f
                ON c.company_id = f.company_id

            GROUP BY
                c.company_id,
                c.company_name

            ORDER BY
                job_count DESC,
                c.company_name
            """
        )

        rows = cursor.fetchall()

        companies = [
            {
                "company_id": row[0],
                "company_name": row[1],
                "job_count": row[2]
            }
            for row in rows
        ]

        return {
            "count": len(companies),
            "companies": companies
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# GET LOCATIONS
# --------------------------------------------------

@app.get("/locations")
def get_locations():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                l.location_id,
                l.location_name,
                COUNT(f.job_id) AS job_count

            FROM public.dim_location l

            LEFT JOIN public.fact_jobs f
                ON l.location_id = f.location_id

            GROUP BY
                l.location_id,
                l.location_name

            ORDER BY
                job_count DESC,
                l.location_name
            """
        )

        rows = cursor.fetchall()

        locations = [
            {
                "location_id": row[0],
                "location_name": row[1],
                "job_count": row[2]
            }
            for row in rows
        ]

        return {
            "count": len(locations),
            "locations": locations
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# MARKET TRENDS
# --------------------------------------------------

@app.get("/market/trends")
def get_market_trends():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            WITH monthly_jobs AS (

                SELECT
                    DATE_TRUNC(
                        'month',
                        created_at
                    )::date AS month,

                    COUNT(DISTINCT job_id)
                    AS job_count

                FROM public.fact_jobs

                WHERE created_at IS NOT NULL

                GROUP BY
                    DATE_TRUNC(
                        'month',
                        created_at
                    )
            ),

            trends AS (

                SELECT
                    month,
                    job_count,

                    LAG(job_count)
                    OVER (
                        ORDER BY month
                    )
                    AS previous_month_jobs

                FROM monthly_jobs
            )

            SELECT
                month,
                job_count,
                previous_month_jobs,

                CASE

                    WHEN previous_month_jobs IS NULL
                         OR previous_month_jobs = 0

                    THEN NULL

                    ELSE ROUND(
                        (
                            (
                                job_count
                                - previous_month_jobs
                            )::numeric

                            / previous_month_jobs
                        ) * 100,
                        2
                    )

                END AS growth_percent

            FROM trends

            ORDER BY month
            """
        )

        rows = cursor.fetchall()

        trends = [
            {
                "month": row[0].isoformat(),
                "job_count": row[1],
                "previous_month_jobs": row[2],
                "growth_percent": (
                    float(row[3])
                    if row[3] is not None
                    else None
                )
            }
            for row in rows
        ]

        return {
            "count": len(trends),
            "trends": trends
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==================================================
# JOB MATCHING
# ==================================================

@app.post("/match")
def match_jobs(candidate: CandidateRequest):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # --------------------------------------------------
        # BUILD FILTERED JOB QUERY
        # --------------------------------------------------

        query = """
            SELECT
                fj.job_id,
                fj.title,
                dc.company_name,
                dl.location_name

            FROM public.fact_jobs fj

            LEFT JOIN public.dim_company dc
                ON fj.company_id = dc.company_id

            LEFT JOIN public.dim_location dl
                ON fj.location_id = dl.location_id

            WHERE 1=1
        """

        params = []

        # --------------------------------------------------
        # ROLE FILTER
        # --------------------------------------------------

        if (
            candidate.role
            and candidate.role.lower() != "all roles"
        ):

            query += """
                AND fj.title ILIKE %s
            """

            params.append(
                f"%{candidate.role}%"
            )

        # --------------------------------------------------
        # LOCATION FILTER
        # --------------------------------------------------

        if (
            candidate.location
            and candidate.location.lower()
            != "all locations"
        ):

            query += """
                AND dl.location_name ILIKE %s
            """

            params.append(
                f"%{candidate.location}%"
            )

        # --------------------------------------------------
        # EXECUTE FILTERED QUERY
        # --------------------------------------------------

        cursor.execute(
            query,
            params
        )

        jobs = cursor.fetchall()

        # --------------------------------------------------
        # CANDIDATE SKILLS
        # --------------------------------------------------

        candidate_skills = {
            skill.strip().lower()
            for skill in candidate.skills
            if skill
        }

        # --------------------------------------------------
        # RESULT LISTS
        # --------------------------------------------------

        recommended_results = []

        all_results = []

        jobs_with_skill_data = 0

        # ==================================================
        # PROCESS EVERY FILTERED JOB
        # ==================================================

        for (
            job_id,
            title,
            company_name,
            location_name
        ) in jobs:

            # --------------------------------------------------
            # GET JOB SKILLS
            # --------------------------------------------------

            cursor.execute(
                """
                SELECT ds.skill_name

                FROM public.job_skills js

                JOIN public.dim_skill ds
                    ON js.skill_id = ds.skill_id

                WHERE js.job_id = %s
                """,
                (job_id,)
            )

            job_skills = [
                row[0]
                for row in cursor.fetchall()
            ]

            # --------------------------------------------------
            # JOB WITHOUT SKILL DATA
            # --------------------------------------------------

            if not job_skills:

                all_results.append(
                    {
                        "job_id": job_id,
                        "title": title,
                        "company": company_name,
                        "location": location_name,
                        "match_score": None,
                        "matched_skills": [],
                        "missing_skills": [],
                        "skill_data_available": False
                    }
                )

                continue

            # --------------------------------------------------
            # JOB HAS SKILL DATA
            # --------------------------------------------------

            jobs_with_skill_data += 1

            normalized_job_skills = {
                skill.strip().lower()
                for skill in job_skills
                if skill
            }

            # --------------------------------------------------
            # MATCHED SKILLS
            # --------------------------------------------------

            matched_skills = (
                candidate_skills
                & normalized_job_skills
            )

            # --------------------------------------------------
            # MISSING SKILLS
            # --------------------------------------------------

            missing_skills = (
                normalized_job_skills
                - candidate_skills
            )

            # --------------------------------------------------
            # MATCH SCORE
            # --------------------------------------------------

            if normalized_job_skills:

                match_score = round(
                    (
                        len(matched_skills)
                        / len(normalized_job_skills)
                    ) * 100
                )

            else:

                match_score = 0

            # --------------------------------------------------
            # CREATE JOB RESULT
            # --------------------------------------------------

            job_result = {

                "job_id": job_id,

                "title": title,

                "company": company_name,

                "location": location_name,

                "match_score": match_score,

                "matched_skills": sorted(
                    matched_skills
                ),

                "missing_skills": sorted(
                    missing_skills
                ),

                "skill_data_available": True
            }

            # --------------------------------------------------
            # ADD TO ALL RESULTS
            # --------------------------------------------------

            all_results.append(
                job_result
            )

            # --------------------------------------------------
            # ADD TO RECOMMENDATION RESULTS
            # --------------------------------------------------

            recommended_results.append(
                job_result
            )

        # ==================================================
        # SORT ALL RESULTS
        # ==================================================

        # Jobs with skill data are sorted by match score so that
        # the most relevant jobs appear first in recommendations.
        recommended_results.sort(
            key=lambda x: x["match_score"],
            reverse=True
        )

        # --------------------------------------------------
        # FILTER RECOMMENDATIONS
        # --------------------------------------------------

        # Only recommend jobs with at least one matching skill.
        # Jobs with 0% match remain available in all_results.
        recommended_results = [
            job
            for job in recommended_results
            if job["match_score"] > 0
        ]

        # Show only the top 20 most relevant jobs.
        top_recommendations = recommended_results[:20]

        # ==================================================
        # RESPONSE
        # ==================================================

        return {

            "candidate_skills": candidate.skills,

            "filters": {

                "role": candidate.role,

                "location": candidate.location,

                "experience": candidate.experience,

                "salary": candidate.salary
            },

            # Total jobs matching role/location filters.
            "jobs_found": len(jobs),

            # Jobs for which skill data was available and a
            # match score could be calculated.
            "jobs_with_skill_data": jobs_with_skill_data,

            # Same meaning as jobs_with_skill_data: these are
            # the jobs actually analyzed for skill matching.
            "jobs_analyzed": jobs_with_skill_data,

            # Top 20 relevant jobs only.
            "results": top_recommendations,

            # Every job matching the selected filters, including
            # jobs with no extracted skill data.
            "all_results": all_results
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()