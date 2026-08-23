from adzuna_client import AdzunaClient


client = AdzunaClient()

data = client.search_jobs(
    country="in",
    page=1,
    keyword="data analyst",
    results_per_page=5,
)

print("Total matching jobs:", data.get("count"))
print("Jobs returned:", len(data.get("results", [])))

for job in data.get("results", []):
    print(
        job.get("title"),
        "|",
        job.get("company", {}).get("display_name"),
        "|",
        job.get("location", {}).get("display_name"),
    )