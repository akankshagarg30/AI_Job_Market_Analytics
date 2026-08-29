import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI Job Market Analytics",
    page_icon="📊",
    layout="wide"
)


st.title("📊 AI Job Market Analytics")

st.markdown(
    "Find and explore jobs based on your preferences."
)

st.divider()

st.subheader("🔎 Job Search")

col1, col2 = st.columns(2)

with col1:

    job_role = st.selectbox(
        "Job Role",
        [
            "Data Analyst",
            "Data Scientist",
            "Data Engineer",
            "Business Analyst"
        ]
    )

    location = st.selectbox(
        "Location",
        [
            "All Locations",
            "Bangalore",
            "Pune",
            "Mumbai",
            "Delhi",
            "Hyderabad"
        ]
    )


with col2:

    experience = st.selectbox(
        "Experience",
        [
            "Any Experience",
            "0–3 Years",
            "3–5 Years",
            "5+ Years"
        ]
    )

    salary = st.selectbox(
        "Salary",
        [
            "Any Salary",
            "₹5L+",
            "₹8L+",
            "₹10L+"
        ]
    )


st.divider()


if st.button("🔍 SEARCH JOBS", type="primary"):

    try:

        response = requests.get(
            f"{API_URL}/jobs",
            params={
                "role": job_role,
                "location": location
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        jobs = data.get("jobs", [])

        st.success(
            f"Found {len(jobs)} matching jobs"
        )

        st.divider()

        st.subheader("💼 Recommended Jobs")


        if not jobs:

            st.warning(
                "No jobs found for the selected filters."
            )

        else:

            for job in jobs:

                title = job.get(
                    "title",
                    "Job title unavailable"
                )

                job_id = job.get(
                    "job_id",
                    "N/A"
                )
                
                company_name = job.get(
    "company_name",
    "Company not specified"
)

                location_name = job.get(
    "location_name",
    "Location not specified"
)

                description = job.get(
                    "description",
                    "No description available."
                )

                contract_time = job.get(
                    "contract_time",
                    "Not specified"
                )

                job_url = job.get(
                    "job_url"
                )


                with st.container(border=True):

                    st.markdown(
                        f"### {title}"
                    )

                    st.caption(
    f"🏢 {company_name}  •  📍 {location_name}"
)

                    st.caption(
    f"Job ID: {job_id}"
)

                    st.write(
                        f"**Employment Type:** "
                        f"{contract_time}"
                    )

                    st.write(
                        description[:500] + "..."
                        if description
                        else "No description available."
                    )


                    if job_url:

                        st.link_button(
                            "View Job",
                            job_url
                        )


    except requests.exceptions.RequestException as e:

        st.error(
            "Unable to connect to the FastAPI backend."
        )

        st.code(str(e))