import csv
from collections import Counter
from pathlib import Path


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skills.csv"
)


# --------------------------------------------------
# COUNT SKILLS
# --------------------------------------------------

skill_counts = Counter()

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:
        skill_counts[row["skill"]] += 1


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

print("=" * 60)
print("SKILL DEMAND ANALYSIS")
print("=" * 60)

print()

for skill, count in skill_counts.most_common():

    print(
        f"{skill:<25} {count:>5} jobs"
    )