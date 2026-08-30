from src.resume_extractor import extract_resume_information


def test_extract_resume_information():

    resume_text = """
    SKILLS
    SQL, Python, Power BI, Excel

    EXPERIENCE
    Data Analyst at ABC Company
    2 years of experience

    EDUCATION
    Bachelor of Technology in Computer Science

    PROJECTS
    Sales Dashboard using Power BI
    Customer Analysis using SQL and Python

    CERTIFICATIONS
    Google Cloud Associate Cloud Engineer
    AWS Certified Data Engineer
    """

    result = extract_resume_information(resume_text)

    assert isinstance(result, dict)

    assert "skills" in result
    assert "experience" in result
    assert "education" in result
    assert "projects" in result
    assert "certifications" in result


def test_empty_resume():

    result = extract_resume_information("")

    assert isinstance(result, dict)

    assert result["skills"] == []