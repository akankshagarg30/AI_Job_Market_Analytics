from src.matching import calculate_match_score


def test_skill_matching():

    candidate_skills = [
        "SQL",
        "Python",
        "Power BI",
        "Excel"
    ]

    job_skills = [
        "SQL",
        "Python",
        "Power BI",
        "Tableau",
        "AWS"
    ]

    result = calculate_match_score(
        candidate_skills,
        job_skills
    )

    assert result["match_score"] == 60
    assert set(result["matched_skills"]) == {
        "sql",
        "python",
        "power bi"
    }
    assert set(result["missing_skills"]) == {
        "tableau",
        "aws"
    }