-- ============================================================
-- AI JOB MARKET ANALYTICS
-- SQL ANALYSIS
-- ============================================================

-- 1. Total Jobs
SELECT
    COUNT(*) AS total_jobs
FROM fact_jobs;


-- 2. Jobs by Search Role
SELECT
    search_role,
    COUNT(*) AS job_count
FROM fact_jobs
GROUP BY search_role
ORDER BY job_count DESC;


-- 3. Top Companies
SELECT
    c.company_name,
    COUNT(*) AS job_count
FROM fact_jobs j
JOIN dim_company c
    ON j.company_id = c.company_id
GROUP BY c.company_name
ORDER BY job_count DESC
LIMIT 15;


-- 4. Top Job Locations
SELECT
    l.location_name,
    COUNT(*) AS job_count
FROM fact_jobs j
JOIN dim_location l
    ON j.location_id = l.location_id
GROUP BY l.location_name
ORDER BY job_count DESC
LIMIT 15;


-- 5. Most Demanded Skills
SELECT
    s.skill_name,
    COUNT(DISTINCT js.job_id) AS job_count
FROM job_skills js
JOIN dim_skill s
    ON js.skill_id = s.skill_id
GROUP BY s.skill_name
ORDER BY job_count DESC;


-- 6. Skill Demand %
SELECT
    s.skill_name,

    COUNT(DISTINCT js.job_id) AS job_count,

    ROUND(
        COUNT(DISTINCT js.job_id) * 100.0
        / (SELECT COUNT(*) FROM fact_jobs),
        2
    ) AS demand_percentage

FROM job_skills js

JOIN dim_skill s
    ON js.skill_id = s.skill_id

GROUP BY s.skill_name

ORDER BY demand_percentage DESC;


-- 7. Skills by Job Role
SELECT
    j.search_role,
    s.skill_name,
    COUNT(DISTINCT j.job_id) AS job_count

FROM fact_jobs j

JOIN job_skills js
    ON j.job_id = js.job_id

JOIN dim_skill s
    ON js.skill_id = s.skill_id

GROUP BY
    j.search_role,
    s.skill_name

ORDER BY
    j.search_role,
    job_count DESC;


-- 8. Top Skills by Role
WITH skill_counts AS (

    SELECT
        j.search_role,
        s.skill_name,
        COUNT(DISTINCT j.job_id) AS job_count

    FROM fact_jobs j

    JOIN job_skills js
        ON j.job_id = js.job_id

    JOIN dim_skill s
        ON js.skill_id = s.skill_id

    GROUP BY
        j.search_role,
        s.skill_name
),

ranked_skills AS (

    SELECT
        *,
        RANK() OVER (
            PARTITION BY search_role
            ORDER BY job_count DESC
        ) AS skill_rank

    FROM skill_counts
)

SELECT
    search_role,
    skill_name,
    job_count
FROM ranked_skills
WHERE skill_rank <= 5
ORDER BY
    search_role,
    skill_rank;


-- 9. Companies by Role
SELECT
    j.search_role,
    c.company_name,
    COUNT(*) AS job_count

FROM fact_jobs j

JOIN dim_company c
    ON j.company_id = c.company_id

GROUP BY
    j.search_role,
    c.company_name

ORDER BY
    j.search_role,
    job_count DESC;


-- 10. Data Analyst Skill Demand
SELECT
    s.skill_name,

    COUNT(DISTINCT j.job_id) AS job_count,

    ROUND(
        COUNT(DISTINCT j.job_id) * 100.0
        /
        (
            SELECT COUNT(*)
            FROM fact_jobs
            WHERE search_role = 'data analyst'
        ),
        2
    ) AS demand_percentage

FROM fact_jobs j

JOIN job_skills js
    ON j.job_id = js.job_id

JOIN dim_skill s
    ON js.skill_id = s.skill_id

WHERE j.search_role = 'data analyst'

GROUP BY s.skill_name

ORDER BY demand_percentage DESC;