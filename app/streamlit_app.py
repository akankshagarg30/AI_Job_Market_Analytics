import requests
import streamlit as st


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AI Job Market Analytics",
    page_icon="📊",
    layout="wide"
)


# ==================================================
# API CONFIGURATION
# ==================================================

API_URL = "http://127.0.0.1:8000"


# ==================================================
# SESSION STATE
# ==================================================

if "search_data" not in st.session_state:

    st.session_state.search_data = None


if "show_all_jobs" not in st.session_state:

    st.session_state.show_all_jobs = False


# ==================================================
# PAGE HEADER
# ==================================================

st.title("AI Job Market Analytics")

st.markdown(
    "Find and explore jobs based on your preferences."
)

st.divider()


# ==================================================
# JOB SEARCH FILTERS
# ==================================================

st.subheader("Job Search")

col1, col2 = st.columns(2)


with col1:

    job_role = st.selectbox(
        "Job Role",
        [
            "Select a job role",
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


# ==================================================
# CANDIDATE SKILLS
# ==================================================

st.divider()

st.subheader("Your Skills")


candidate_skills = st.multiselect(
    "Select your skills",
    [
        "SQL",
        "Python",
        "Power BI",
        "Excel",
        "Tableau",
        "R",
        "AWS",
        "Azure",
        "Google Cloud",
        "Snowflake",
        "Databricks",
        "Apache Spark",
        "Machine Learning",
        "Deep Learning",
        "NLP",
        "Statistics",
        "ETL",
        "Data Visualization",
        "Git",
        "Java",
        "C++",
        "JavaScript"
    ]
)


# ==================================================
# SEARCH BUTTON
# ==================================================

st.divider()


if st.button(
    "SEARCH JOBS",
    type="primary"
):

    # --------------------------------------------------
    # CHECK SKILLS
    # --------------------------------------------------

    if job_role == "Select a job role":

        st.warning(
            "Please select a job role."
        )
    elif not candidate_skills:
        st.warning("Please select at least one skill.")

    else:

        try:

            # --------------------------------------------------
            # CALL FASTAPI
            # --------------------------------------------------

            response = requests.post(

                f"{API_URL}/match",

                json={

                    "skills": candidate_skills,

                    "role": job_role,

                    "location": location,

                    "experience": experience,

                    "salary": salary
                },

                timeout=30
            )

            # --------------------------------------------------
            # SUCCESS
            # --------------------------------------------------

            if response.status_code == 200:

                data = response.json()

                # Save results so Streamlit reruns
                # do not lose them.

                st.session_state.search_data = data

                # Return to recommendations
                # whenever a new search is performed.

                st.session_state.show_all_jobs = False

                st.rerun()

            # --------------------------------------------------
            # API ERROR
            # --------------------------------------------------

            else:

                st.error(
                    f"API error: "
                    f"{response.status_code}"
                )

        # ------------------------------------------------------
        # FASTAPI NOT RUNNING
        # ------------------------------------------------------

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to FastAPI. "
                "Make sure the API is running."
            )

        # ------------------------------------------------------
        # OTHER ERROR
        # ------------------------------------------------------

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )


# ==================================================
# DISPLAY SEARCH RESULTS
# ==================================================

if st.session_state.search_data:

    data = st.session_state.search_data

    results = data.get(
        "results",
        []
    )

    all_results = data.get(
        "all_results",
        []
    )

    jobs_found = data.get(
        "jobs_found",
        0
    )

    jobs_analyzed = data.get(
        "jobs_analyzed",
        0
    )

    jobs_with_skill_data = data.get(
        "jobs_with_skill_data",
        jobs_analyzed
    )


    # ==================================================
    # SEARCH SUMMARY
    # ==================================================

    recommended_count = len(data.get("results", []))

    st.success(
        f"{data['jobs_found']} jobs found | "
        f"{recommended_count} relevant jobs"
    )


    # ==================================================
    # RECOMMENDED JOBS
    # ==================================================

    st.divider()

    st.subheader(
        "Recommended Jobs"
    )

    st.caption(
        "Top jobs ranked by your skill match."
    )


    # --------------------------------------------------
    # NO RECOMMENDATIONS
    # --------------------------------------------------

    if not results:

        st.info(
            "No recommended jobs found."
        )


    # --------------------------------------------------
    # DISPLAY RECOMMENDATIONS
    # --------------------------------------------------

    else:

        for job in results:

            st.markdown(
                f"### {job['title']}"
            )

            st.write(
                f"**Company:** "
                f"{job['company']}"
            )

            st.write(
                f"**Location:** "
                f"{job['location']}"
            )

            # ----------------------------------------------
            # MATCH SCORE
            # ----------------------------------------------

            st.metric(
                "Match Score",
                f"{job['match_score']}%"
            )


            # ----------------------------------------------
            # MATCHED SKILLS
            # ----------------------------------------------

            if job["matched_skills"]:

                st.write(
                    "**Matched Skills:** "
                    + ", ".join(
                        job["matched_skills"]
                    )
                )


            # ----------------------------------------------
            # MISSING SKILLS
            # ----------------------------------------------

            if job["missing_skills"]:

                st.write(
                    "**Missing Skills:** "
                    + ", ".join(
                        job["missing_skills"]
                    )
                )


            st.divider()


    # ==================================================
    # EXPLORE ALL JOBS
    # ==================================================

    st.markdown(
        "## 🔎 Explore All Matching Jobs"
    )

    st.write(
        f"**{jobs_found} jobs** are available "
        "for your selected filters."
    )


    # ==================================================
    # VIEW ALL BUTTON
    # ==================================================

    if not st.session_state.show_all_jobs:

        if st.button(
            "VIEW ALL MATCHING JOBS",
            type="secondary"
        ):

            st.session_state.show_all_jobs = True

            st.rerun()


    # ==================================================
    # ALL JOBS SECTION
    # ==================================================

    if st.session_state.show_all_jobs:

        st.divider()

        st.subheader(
            f"All Matching Jobs ({len(all_results)})"
        )

        st.caption(
            "These are all jobs matching your selected "
            "role and location filters."
        )


        # --------------------------------------------------
        # BACK BUTTON
        # --------------------------------------------------

        if st.button(
            "← BACK TO RECOMMENDED JOBS"
        ):

            st.session_state.show_all_jobs = False

            st.rerun()


        st.divider()


        # ==================================================
        # DISPLAY ALL JOBS
        # ==================================================

        if not all_results:

            st.info(
                "No jobs found for the selected filters."
            )

        else:

            for index, job in enumerate(
                all_results,
                start=1
            ):

                st.markdown(
                    f"### {index}. {job['title']}"
                )

                st.write(
                    f"**Company:** "
                    f"{job['company']}"
                )

                st.write(
                    f"**Location:** "
                    f"{job['location']}"
                )


                # --------------------------------------------------
                # SKILL DATA AVAILABLE
                # --------------------------------------------------

                if job.get(
                    "skill_data_available",
                    False
                ):

                    st.metric(
                        "Match Score",
                        f"{job['match_score']}%"
                    )


                    if job["matched_skills"]:

                        st.write(
                            "**Matched Skills:** "
                            + ", ".join(
                                job["matched_skills"]
                            )
                        )


                    if job["missing_skills"]:

                        st.write(
                            "**Missing Skills:** "
                            + ", ".join(
                                job["missing_skills"]
                            )
                        )


                # --------------------------------------------------
                # NO SKILL DATA
                # --------------------------------------------------

                else:

                    st.info(
                        "Skill data not available "
                        "for this job."
                    )


                st.divider()