"""
Analytics helper functions for the AI Job Market Analytics project.

These functions work with the job dictionaries already returned by the
existing application/API. No API changes are required.
"""

from collections import Counter
from typing import Any


def _safe_jobs(jobs: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Return only valid job dictionaries."""
    if not jobs:
        return []
    return [job for job in jobs if isinstance(job, dict)]


def _clean_text(value: Any) -> str:
    """Convert a value to clean text."""
    if value is None:
        return ""
    return str(value).strip()


def get_total_jobs(jobs: list[dict[str, Any]] | None) -> int:
    """Return the number of jobs."""
    return len(_safe_jobs(jobs))


def get_jobs_with_skill_data(
    jobs: list[dict[str, Any]] | None,
) -> int:
    """Return jobs for which skill data is available."""
    return sum(
        1
        for job in _safe_jobs(jobs)
        if job.get("skill_data_available", True)
        and (
            job.get("matched_skills")
            or job.get("missing_skills")
            or job.get("match_score") is not None
        )
    )


def get_average_match_score(
    jobs: list[dict[str, Any]] | None,
) -> float:
    """Return the average available resume match score."""
    scores = []

    for job in _safe_jobs(jobs):
        score = job.get("match_score")

        if isinstance(score, (int, float)):
            scores.append(float(score))

    if not scores:
        return 0.0

    return round(sum(scores) / len(scores), 2)


def get_jobs_by_location(
    jobs: list[dict[str, Any]] | None,
) -> dict[str, int]:
    """Return job counts grouped by location."""
    counts = Counter()

    for job in _safe_jobs(jobs):
        location = _clean_text(job.get("location"))

        if location:
            counts[location] += 1

    return dict(counts.most_common())


def get_jobs_by_role(
    jobs: list[dict[str, Any]] | None,
) -> dict[str, int]:
    """
    Return job counts grouped by normalized job title.

    Job titles that differ only by capitalization or extra whitespace
    are treated as the same role.
    """
    counts = Counter()

    for job in _safe_jobs(jobs):
        title = _clean_text(job.get("title"))

        if not title:
            continue

        # Normalize whitespace and capitalization for grouping.
        normalized = " ".join(title.split()).casefold()

        # Professional display labels for common roles.
        display_title = {
            "data analyst": "Data Analyst",
            "data scientist": "Data Scientist",
            "data engineer": "Data Engineer",
            "business analyst": "Business Analyst",
        }.get(
            normalized,
            " ".join(title.split()).title()
        )

        counts[display_title] += 1

    return dict(counts.most_common())


def get_top_skills(
    jobs: list[dict[str, Any]] | None,
    top_n: int = 10,
) -> list[tuple[str, int]]:
    """
    Return the most frequently requested skills.

    The current API response exposes skills through `matched_skills`
    and `missing_skills`. Their union represents the skills associated
    with a job that has skill data.
    """
    if top_n <= 0:
        return []

    counts = Counter()

    for job in _safe_jobs(jobs):
        skills = set()

        for field in ("matched_skills", "missing_skills"):
            values = job.get(field, [])

            if isinstance(values, (list, tuple, set)):
                for skill in values:
                    cleaned = _clean_text(skill).lower()

                    if cleaned:
                        skills.add(cleaned)

        for skill in skills:
            counts[skill] += 1

    return counts.most_common(top_n)


def get_match_score_distribution(
    jobs: list[dict[str, Any]] | None,
) -> dict[str, int]:
    """Group jobs into resume-match score ranges."""
    distribution = {
        "90-100%": 0,
        "80-89%": 0,
        "70-79%": 0,
        "60-69%": 0,
        "50-59%": 0,
        "Below 50%": 0,
    }

    for job in _safe_jobs(jobs):
        score = job.get("match_score")

        if not isinstance(score, (int, float)):
            continue

        score = float(score)

        if score >= 90:
            distribution["90-100%"] += 1
        elif score >= 80:
            distribution["80-89%"] += 1
        elif score >= 70:
            distribution["70-79%"] += 1
        elif score >= 60:
            distribution["60-69%"] += 1
        elif score >= 50:
            distribution["50-59%"] += 1
        else:
            distribution["Below 50%"] += 1

    return distribution


def get_top_missing_skills(
    jobs: list[dict[str, Any]] | None,
    top_n: int = 10,
    minimum_match_score: int = 50,
) -> list[tuple[str, int]]:
    """
    Return skills most frequently missing from relevant jobs.

    This is useful for the personalized skill-development section.
    Only jobs at or above `minimum_match_score` are considered.
    """
    if top_n <= 0:
        return []

    counts = Counter()

    for job in _safe_jobs(jobs):
        score = job.get("match_score")

        if not isinstance(score, (int, float)):
            continue

        if score < minimum_match_score:
            continue

        missing_skills = job.get("missing_skills", [])

        if not isinstance(missing_skills, (list, tuple, set)):
            continue

        skills = {
            _clean_text(skill).lower()
            for skill in missing_skills
            if _clean_text(skill)
        }

        for skill in skills:
            counts[skill] += 1

    return counts.most_common(top_n)
