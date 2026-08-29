import csv
from pathlib import Path

from skill_dictionary import SKILLS


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_clean.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skills.csv"
)


# --------------------------------------------------
# EXTRACT SKILLS
# --------------------------------------------------

def extract_skills(text):

    text = (text or "").lower()

    found_skills = []

    for skill, keywords in SKILLS.items():

        for keyword in keywords:

            if keyword in text:

                found_skills.append(skill)

                break

    return found_skills


# --------------------------------------------------
# PROCESS JOBS
# --------------------------------------------------

skill_records = []

processed_jobs = 0
jobs_with_skills = 0


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for job in reader:

        processed_jobs += 1

        description = job.get(
            "description",
            ""
        )

        skills = extract_skills(
            description
        )

        if skills:
            jobs_with_skills += 1

        for skill in skills:

            skill_records.append({

                "job_id": job["job_id"],

                "skill": skill,

            })


# --------------------------------------------------
# SAVE SKILL DATA
# --------------------------------------------------

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "job_id",
            "skill"
        ]
    )

    writer.writeheader()

    writer.writerows(
        skill_records
    )


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print("=" * 60)
print("SKILL EXTRACTION COMPLETE")
print("=" * 60)

print(
    "Jobs processed:",
    processed_jobs
)

print(
    "Jobs containing at least one skill:",
    jobs_with_skills
)

print(
    "Job-skill records created:",
    len(skill_records)
)

print()
print("Saved to:")
print(OUTPUT_FILE)