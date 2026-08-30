from src.analytics import (
    get_average_match_score,
    get_jobs_by_location,
    get_jobs_by_role,
    get_match_score_distribution,
    get_top_missing_skills,
    get_top_skills,
    get_total_jobs,
)


JOBS = [
    {
        "title": "Data Analyst",
        "location": "Bangalore, India",
        "match_score": 90,
        "matched_skills": ["SQL", "Python"],
        "missing_skills": ["Tableau"],
    },
    {
        "title": "Data Analyst",
        "location": "Hyderabad, Telangana",
        "match_score": 70,
        "matched_skills": ["SQL"],
        "missing_skills": ["Python", "Power BI"],
    },
    {
        "title": "Business Analyst",
        "location": "Bangalore, India",
        "match_score": 55,
        "matched_skills": ["SQL"],
        "missing_skills": ["Tableau"],
    },
    {
        "title": "Data Engineer",
        "location": "Mumbai, Maharashtra",
        "match_score": 30,
        "matched_skills": ["Python"],
        "missing_skills": ["AWS"],
    },
]


def test_get_total_jobs():
    assert get_total_jobs(JOBS) == 4


def test_get_average_match_score():
    assert get_average_match_score(JOBS) == 61.25


def test_get_jobs_by_location():
    assert get_jobs_by_location(JOBS) == {
        "Bangalore, India": 2,
        "Hyderabad, Telangana": 1,
        "Mumbai, Maharashtra": 1,
    }


def test_get_jobs_by_role():
    assert get_jobs_by_role(JOBS) == {
        "Data Analyst": 2,
        "Business Analyst": 1,
        "Data Engineer": 1,
    }


def test_get_top_skills():
    result = get_top_skills(JOBS, top_n=3)

    assert len(result) == 3

    assert result[0][1] == 3
    assert result[1][1] == 3
    assert result[2] == ("tableau", 2)

    assert {
        result[0][0],
        result[1][0],
    } == {
        "sql",
        "python",
    }


def test_get_match_score_distribution():
    result = get_match_score_distribution(JOBS)

    assert result == {
        "90-100%": 1,
        "80-89%": 0,
        "70-79%": 1,
        "60-69%": 0,
        "50-59%": 1,
        "Below 50%": 1,
    }


def test_get_top_missing_skills():
    result = get_top_missing_skills(
        JOBS,
        top_n=3,
        minimum_match_score=50,
    )

    assert result[0] == ("tableau", 2)

    assert set(result[1:]) == {
        ("python", 1),
        ("power bi", 1),
    }


def test_empty_jobs():
    assert get_total_jobs([]) == 0
    assert get_average_match_score([]) == 0.0
    assert get_jobs_by_location([]) == {}
    assert get_jobs_by_role([]) == {}
    assert get_top_skills([]) == []
    assert get_match_score_distribution([]) == {
        "90-100%": 0,
        "80-89%": 0,
        "70-79%": 0,
        "60-69%": 0,
        "50-59%": 0,
        "Below 50%": 0,
    }
