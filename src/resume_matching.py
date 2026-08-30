def calculate_match_summary(jobs: list[dict]) -> dict:
    """
    Calculate resume-to-job match statistics.

    Match categories:
        75% - 100% : Strong Match
        50% - 74%  : Moderate Match
        Below 50%  : Low Match
    """

    strong_match = 0
    moderate_match = 0
    low_match = 0

    for job in jobs:

        try:
            score = float(
                job.get("match_score", 0) or 0
            )
        except (TypeError, ValueError):
            score = 0

        if score >= 75:
            strong_match += 1

        elif score >= 50:
            moderate_match += 1

        else:
            low_match += 1

    return {
        "jobs_analyzed": len(jobs),
        "strong_match": strong_match,
        "moderate_match": moderate_match,
        "low_match": low_match,
    }
    
from collections import Counter


def get_top_missing_skills(
    jobs: list[dict],
    top_n: int = 5
) -> list[dict]:
    """
    Find the most frequently missing skills
    across relevant jobs.

    Only jobs with a match score of 50% or higher
    are considered relevant.
    """

    skill_counter = Counter()

    for job in jobs:

        try:
            score = float(
                job.get("match_score", 0) or 0
            )
        except (TypeError, ValueError):
            score = 0

        # Consider only relevant jobs
        if score < 50:
            continue

        missing_skills = job.get(
            "missing_skills",
            []
        )

        for skill in missing_skills:

            if skill:

                skill_counter[
                    skill.strip()
                ] += 1

    top_skills = skill_counter.most_common(
        top_n
    )

    return [
        {
            "skill": skill,
            "job_count": count
        }
        for skill, count in top_skills
    ]