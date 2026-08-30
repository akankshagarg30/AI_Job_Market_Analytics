from typing import List, Dict


def calculate_match_score(
    candidate_skills: List[str],
    job_skills: List[str]
) -> Dict:
    """
    Calculate how well a candidate's skills match a job.
    """

    # Normalize skills
    candidate = {
        skill.strip().lower()
        for skill in candidate_skills
        if skill
    }

    job = {
        skill.strip().lower()
        for skill in job_skills
        if skill
    }

    # Avoid division by zero
    if not job:
        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": job_skills
        }

    # Find common skills
    matched = candidate.intersection(job)

    # Skills required by job but missing from candidate
    missing = job - candidate

    # Calculate percentage
    match_score = round(
        (len(matched) / len(job)) * 100
    )

    return {
        "match_score": match_score,
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing)
    }