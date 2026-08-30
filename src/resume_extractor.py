import re


# ============================================================
# KNOWN SKILLS
# ============================================================

KNOWN_SKILLS = [
    "SQL",
    "Python",
    "Power BI",
    "Excel",
    "Tableau",
    "R",
    "AWS",
    "Azure",
    "Google Cloud",
    "Google Cloud Platform",
    "Snowflake",
    "Databricks",
    "Apache Spark",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "Natural Language Processing",
    "Statistics",
    "ETL",
    "Data Visualization",
    "Git",
    "Java",
    "C++",
    "JavaScript",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Spring Boot",
    "Spring Data JPA",
    "ReactJS",
    "React",
    "Tailwind CSS",
    "HTML",
    "CSS",
    "JavaScript",
    "REST API",
    "REST APIs",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "Scikit-learn",
    "TensorFlow",
    "PyTorch",
]


# ============================================================
# SECTION NAMES
# ============================================================

SECTION_NAMES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "objective",
        "career objective",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "work history",
    ],
    "education": [
        "education",
        "academic background",
        "educational background",
        "qualifications",
    ],
    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "key projects",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "professional certifications",
    ],
    "skills": [
        "skills",
        "technical skills",
        "technical skill",
        "skills & technologies",
        "technical expertise",
    ],
    "achievements": [
        "achievements",
        "accomplishments",
        "awards",
    ],
}


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_line(line: str) -> str:
    """
    Clean a single extracted PDF line.
    """

    if not line:
        return ""

    line = line.replace("\u2022", " ")
    line = line.replace("\uf0b7", " ")
    line = line.replace("●", " ")
    line = line.replace("○", " ")
    line = line.replace("▪", " ")
    line = line.replace("◦", " ")

    line = re.sub(r"\s+", " ", line)

    return line.strip(" \t-–—•")


def normalize_text(text: str) -> str:
    """
    Normalize resume text while preserving line structure.
    """

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        cleaned = clean_line(line)

        if cleaned:
            lines.append(cleaned)

    return "\n".join(lines)


# ============================================================
# SECTION DETECTION
# ============================================================

def detect_section(line: str) -> str | None:
    """
    Detect whether a line represents a major resume section.
    """

    if not line:
        return None

    cleaned = clean_line(line).lower()

    # Remove common punctuation
    cleaned = re.sub(r"[:\-–—]+$", "", cleaned).strip()

    for section, names in SECTION_NAMES.items():

        for name in names:

            if cleaned == name.lower():
                return section

    return None


def extract_section_lines(
    text: str,
    section_name: str
) -> list[str]:

    """
    Extract all lines belonging to a particular section.
    """

    normalized_text = normalize_text(text)

    if not normalized_text:
        return []

    lines = normalized_text.splitlines()

    collected = []
    current_section = None

    for line in lines:

        detected = detect_section(line)

        if detected:

            current_section = detected
            continue

        if current_section == section_name:

            collected.append(line)

    return collected


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_skills(text: str) -> list[str]:
    """
    Extract known technical skills from resume text.

    Matching is case-insensitive and uses word boundaries
    to avoid false matches.
    """

    if not text:
        return []

    normalized_text = normalize_text(text)

    found_skills = []

    for skill in KNOWN_SKILLS:

        escaped_skill = re.escape(skill)

        pattern = rf"(?<!\w){escaped_skill}(?!\w)"

        if re.search(
            pattern,
            normalized_text,
            flags=re.IGNORECASE
        ):

            # Avoid duplicate concepts such as
            # React / ReactJS
            if skill not in found_skills:
                found_skills.append(skill)

    # --------------------------------------------------------
    # Remove duplicates / overlapping representations
    # --------------------------------------------------------

    if "Google Cloud Platform" in found_skills:
        if "Google Cloud" in found_skills:
            found_skills.remove("Google Cloud Platform")

    if "ReactJS" in found_skills:
        if "React" in found_skills:
            found_skills.remove("React")

    if "REST APIs" in found_skills:
        if "REST API" in found_skills:
            found_skills.remove("REST API")

    if "Natural Language Processing" in found_skills:
        if "NLP" in found_skills:
            found_skills.remove("Natural Language Processing")

    return found_skills


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_experience(text: str) -> str | None:
    """
    Extract the EXPERIENCE section.

    If an explicit number of years is present, it is returned
    as part of the result. Otherwise, the detected experience
    section is returned.
    """

    if not text:
        return None

    normalized_text = normalize_text(text)

    # --------------------------------------------------------
    # First try to find explicit years of experience
    # --------------------------------------------------------

    patterns = [

        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)"
        r"(?:\s+of)?\s+experience",

        r"experience\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            normalized_text,
            flags=re.IGNORECASE
        )

        if match:

            years = match.group(1)

            return f"{years} years of experience"

    # --------------------------------------------------------
    # Otherwise extract EXPERIENCE section
    # --------------------------------------------------------

    experience_lines = extract_section_lines(
        normalized_text,
        "experience"
    )

    if not experience_lines:
        return None

    # Keep the extracted section readable
    return "\n".join(experience_lines)


# ============================================================
# EDUCATION EXTRACTION
# ============================================================

def extract_education(text: str) -> list[str]:
    """
    Extract education information from the EDUCATION section.
    """

    if not text:
        return []

    normalized_text = normalize_text(text)

    education_lines = extract_section_lines(
        normalized_text,
        "education"
    )

    if education_lines:

        cleaned = []

        for line in education_lines:

            if line not in cleaned:
                cleaned.append(line)

        return cleaned

    # --------------------------------------------------------
    # Fallback: detect common qualifications anywhere
    # --------------------------------------------------------

    education_patterns = [
        r"\bB\.?\s*Tech\b",
        r"\bB\.?\s*E\.?\b",
        r"\bB\.?\s*Sc\b",
        r"\bBCA\b",
        r"\bM\.?\s*Tech\b",
        r"\bM\.?\s*E\.?\b",
        r"\bM\.?\s*Sc\b",
        r"\bMCA\b",
        r"\bMBA\b",
        r"\bBachelor(?:'s)?\b",
        r"\bMaster(?:'s)?\b",
        r"\bPh\.?\s*D\b",
    ]

    found = []

    for pattern in education_patterns:

        matches = re.findall(
            pattern,
            normalized_text,
            flags=re.IGNORECASE
        )

        for match in matches:

            if isinstance(match, tuple):
                match = match[0]

            value = match.strip()

            if value and value not in found:
                found.append(value)

    return found


# ============================================================
# CERTIFICATION EXTRACTION
# ============================================================

def extract_certifications(text: str) -> list[str]:
    """
    Extract certifications from the CERTIFICATIONS section.

    The section heading itself is never returned.
    """

    if not text:
        return []

    normalized_text = normalize_text(text)

    certification_lines = extract_section_lines(
        normalized_text,
        "certifications"
    )

    certifications = []

    for line in certification_lines:

        cleaned = clean_line(line)

        if not cleaned:
            continue

        # Ignore another heading accidentally captured
        if detect_section(cleaned) == "certifications":
            continue

        # Ignore generic words
        if cleaned.lower() in {
            "certification",
            "certifications",
            "certificate",
            "certificates",
        }:
            continue

        if cleaned not in certifications:
            certifications.append(cleaned)

    # --------------------------------------------------------
    # Fallback when no certification section exists
    # --------------------------------------------------------

    if not certifications:

        for line in normalized_text.splitlines():

            lower_line = line.lower()

            if (
                "certified" in lower_line
                or "certification" in lower_line
            ):

                if detect_section(line) == "certifications":
                    continue

                if line not in certifications:
                    certifications.append(line)

    return certifications


# ============================================================
# PROJECT EXTRACTION
# ============================================================

def extract_projects(text: str) -> list[str]:
    """
    Extract project information from the PROJECTS section.
    """

    if not text:
        return []

    normalized_text = normalize_text(text)

    project_lines = extract_section_lines(
        normalized_text,
        "projects"
    )

    projects = []

    for line in project_lines:

        cleaned = clean_line(line)

        if not cleaned:
            continue

        # Avoid accidentally including another section heading
        if detect_section(cleaned):
            continue

        if cleaned not in projects:
            projects.append(cleaned)

    return projects


# ============================================================
# MAIN RESUME INFORMATION EXTRACTION
# ============================================================

def extract_resume_information(text: str) -> dict:
    """
    Extract structured information from resume text.

    Returns
    -------
    dict
        {
            "skills": [...],
            "experience": "...",
            "education": [...],
            "projects": [...],
            "certifications": [...]
        }
    """

    if not text:

        return {
            "skills": [],
            "experience": None,
            "education": [],
            "projects": [],
            "certifications": [],
        }

    return {
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "projects": extract_projects(text),
        "certifications": extract_certifications(text),
    }