from fastapi import FastAPI, HTTPException
from src.database.connection import get_connection

app = FastAPI(
    title="AI Job Market Analytics API",
    description="REST API for the AI Job Market Analytics Platform",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "AI Job Market Analytics API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


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

        # Role filter
        if role and role.lower() != "all roles":
            query += """
                AND f.title ILIKE %s
            """
            params.append(f"%{role}%")

        # Location filter
        if location and location.lower() != "all locations":
            query += """
                AND l.location_name ILIKE %s
            """
            params.append(f"%{location}%")

        query += """
            ORDER BY f.created_at DESC
            LIMIT 100
        """

        cursor.execute(query, params)

        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

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

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM public.fact_jobs
            WHERE job_id = %s
        """, (job_id,))

        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        columns = [description[0] for description in cursor.description]

        job = dict(zip(columns, row))

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
            
@app.get("/skills")
def get_skills():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
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
            ORDER BY job_count DESC, s.skill_name
        """)

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
            
@app.get("/skills/top")
def get_top_skills():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                s.skill_name,
                COUNT(DISTINCT js.job_id) AS job_count
            FROM public.dim_skill s
            INNER JOIN public.job_skills js
                ON s.skill_id = js.skill_id
            GROUP BY s.skill_name
            ORDER BY job_count DESC
            LIMIT 10
        """)

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
            
@app.get("/companies")
def get_companies():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
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
            ORDER BY job_count DESC, c.company_name
        """)

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
            
@app.get("/locations")
def get_locations():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
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
            ORDER BY job_count DESC, l.location_name
        """)

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
            
@app.get("/market/trends")
def get_market_trends():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            WITH monthly_jobs AS (
                SELECT
                    DATE_TRUNC('month', created_at)::date AS month,
                    COUNT(DISTINCT job_id) AS job_count
                FROM public.fact_jobs
                WHERE created_at IS NOT NULL
                GROUP BY DATE_TRUNC('month', created_at)
            ),
            trends AS (
                SELECT
                    month,
                    job_count,
                    LAG(job_count) OVER (
                        ORDER BY month
                    ) AS previous_month_jobs
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
                            (job_count - previous_month_jobs)::numeric
                            / previous_month_jobs
                        ) * 100,
                        2
                    )
                END AS growth_percent
            FROM trends
            ORDER BY month;
        """)

        rows = cursor.fetchall()

        trends = [
            {
                "month": row[0].isoformat(),
                "job_count": row[1],
                "previous_month_jobs": row[2],
                "growth_percent": float(row[3]) if row[3] is not None else None
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