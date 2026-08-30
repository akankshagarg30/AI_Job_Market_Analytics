from src.resume_matching import (
    calculate_match_summary,
    get_top_missing_skills
)


def test_calculate_match_summary():

    jobs = [
        {"match_score": 90},
        {"match_score": 80},
        {"match_score": 65},
        {"match_score": 50},
        {"match_score": 30},
    ]

    result = calculate_match_summary(jobs)

    assert result["jobs_analyzed"] == 5
    assert result["strong_match"] == 2
    assert result["moderate_match"] == 2
    assert result["low_match"] == 1
    
def test_get_top_missing_skills():

    jobs = [
        {
            "match_score": 80,
            "missing_skills": [
                "Tableau",
                "Statistics"
            ]
        },
        {
            "match_score": 70,
            "missing_skills": [
                "Tableau",
                "AWS"
            ]
        },
        {
            "match_score": 55,
            "missing_skills": [
                "Tableau"
            ]
        },
        {
            "match_score": 30,
            "missing_skills": [
                "Python",
                "AWS"
            ]
        }
    ]

    result = get_top_missing_skills(
        jobs,
        top_n=3
    )

    assert result[0] == {
        "skill": "Tableau",
        "job_count": 3
    }

    assert result[1] == {
        "skill": "Statistics",
        "job_count": 1
    }

    assert result[2] == {
        "skill": "AWS",
        "job_count": 1
    }