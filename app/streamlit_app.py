import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tempfile

import requests
import streamlit as st
from src.resume_matching import(
    calculate_match_summary,
    get_top_missing_skills
)

from src.analytics import (
    get_total_jobs,
    get_average_match_score,
    get_jobs_by_location,
    get_jobs_by_role,
    get_top_skills,
    get_match_score_distribution,
)

import os

logo_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "assets",
    "joblens_logo.png"
)
# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# RESUME MODULES
# ============================================================

from src.resume_parser import extract_text_from_pdf
from src.resume_extractor import extract_resume_information


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="JobLens AI",
    page_icon=logo_path,
    layout="wide"
)


# ============================================================
# API CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"


# ============================================================
# JOB URL HELPER
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def get_job_url(job_id: str | None) -> str | None:
    """Get the application URL for a job without changing the API."""

    if not job_id:
        return None

    try:
        response = requests.get(
            f"{API_URL}/jobs/{job_id}",
            timeout=10
        )

        if response.status_code == 200:
            job_details = response.json()
            return job_details.get("job_url")

    except requests.RequestException:
        pass

    return None

# ============================================================
# GET FEATURED JOBS
# ============================================================

def get_featured_jobs():
    """
    Get the latest 10 jobs from all roles and locations.
    The API already sorts jobs by created_at DESC.
    """

    try:
        response = requests.get(
            f"{API_URL}/jobs",
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()

            # API returns jobs already ordered by newest first
            return data.get("jobs", [])[:10]

    except requests.RequestException:
        pass

    return []
# ============================================================
# CONSTANTS
# ============================================================

JOB_ROLES = [
    "Select a role",
    "Data Analyst",
    "Data Scientist",
    "Data Engineer",
    "Business Analyst"
]

LOCATIONS = [
    "All Locations",
    "Bangalore",
    "Pune",
    "Mumbai",
    "Delhi",
    "Hyderabad"
]

EXPERIENCE_OPTIONS = [
    "Any Experience",
    "0–3 Years",
    "3–5 Years",
    "5+ Years"
]

SALARY_OPTIONS = [
    "Any Salary",
    "₹5L+",
    "₹8L+",
    "₹10L+"
]

SKILLS = [
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


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "search_data" not in st.session_state:
    st.session_state.search_data = None

if "show_all_jobs" not in st.session_state:
    st.session_state.show_all_jobs = False

if "resume_data" not in st.session_state:
    st.session_state.resume_data = None

if "resume_jobs" not in st.session_state:
    st.session_state.resume_jobs = None

if "resume_filter_min_score" not in st.session_state:
    st.session_state.resume_filter_min_score = "50%+"

if "resume_filter_location" not in st.session_state:
    st.session_state.resume_filter_location = "All Locations"

if "resume_filter_sort" not in st.session_state:
    st.session_state.resume_filter_sort = "Match Score ↓"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:


    # App title
    st.markdown("")

    # App logo
    logo_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "assets",
        "joblens_logo.png"
    )
    st.markdown(
    """
    <style>

    /* Remove extra space around the sidebar logo */
    section[data-testid="stSidebar"] [data-testid="stImage"] {
        margin-top: -40px !important;
        margin-bottom: -35px !important;
        padding: 0 !important;
    }

    /* Logo size */
    section[data-testid="stSidebar"] [data-testid="stImage"] img {
        width: 150px !important;
        height: auto !important;
        display: block !important;
        margin: 0 auto !important;
    }

    /* Reduce space before navigation */
    section[data-testid="stSidebar"] .stRadio {
        margin-top: 0px !important;
        padding-top: 0px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

    st.image(logo_path, use_container_width=True)

    

    # Navigation
    #st.markdown("### Navigation")

    page_options = [
        "Home",
        "Find Job",
        "Analyze Resume",
        "Privacy",
        "Contact Us"
    ]

    page_map = {
        "Home": "Home",
        "Find Job": "Job Search",
        "Analyze Resume": "Resume Analysis",
        "Privacy": "Privacy",
        "Contact Us": "Contact Us"
    }

    current_page_label = next(
        (label for label, value in page_map.items()
         if value == st.session_state.page),
        "Home"
    )
    
    # ============================================================
# PROFESSIONAL SIDEBAR NAVIGATION STYLE
# ============================================================

    st.markdown(
    """
    <style>

    /* Navigation spacing */
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 6px;
    }

    /* Completely remove radio buttons / circles */
    section[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] {
        display: none !important;
    }

    section[data-testid="stSidebar"] .stRadio input[type="radio"] {
        display: none !important;
    }

    /* Navigation cards */
    section[data-testid="stSidebar"] .stRadio label {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        box-sizing: border-box !important;

        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;

        padding: 11px 16px !important;
        margin: 4px 0 !important;

        cursor: pointer !important;
        transition: background-color 0.2s ease !important;
    }

    /* Navigation text */
    section[data-testid="stSidebar"] .stRadio label p {
        margin: 0 !important;
        padding: 0 !important;

        font-size: 16px !important;
        font-weight: 500 !important;

        color: #D1D5DB !important;
    }

    /* Hover effect */
    section[data-testid="stSidebar"] .stRadio label:hover {
        background-color: #30323B !important;
    }

    section[data-testid="stSidebar"] .stRadio label:hover p {
        color: #FFFFFF !important;
    }

    /* Selected navigation card */
    section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background-color: #30323B !important;
        border-color: #3A3D47 !important;
    }

    /* Selected navigation text */
    section[data-testid="stSidebar"] .stRadio label:has(input:checked) p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

    # Keep the radio widget and the actual page state synchronized.
    # No st.rerun() is needed for sidebar navigation.
    page = st.radio(
        "",
        page_options,
        index=page_options.index(current_page_label),
        key="main_navigation",
        label_visibility="collapsed"
    )
    
    selected_page = page_map[page]

        # Analytics is opened from the Job Search page, not from the sidebar.
        # Do not let the sidebar radio overwrite the Analytics page on rerun.
    if st.session_state.page != "Analytics" and st.session_state.page != selected_page:
            st.session_state.page = selected_page

            if selected_page == "Job Search":
                st.session_state.show_all_jobs = False

    st.divider()

    st.caption(
        "AI-Powered Job Market Analytics Platform"
    )
    
# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "Home":

    
    # --------------------------------------------------------
    # --------------------------------------------------------
    # WELCOME SECTION
    # --------------------------------------------------------

    # --------------------------------------------------------
    # CUSTOM CSS
    # --------------------------------------------------------

    st.markdown(
        """
        <style>

        /* ==================================================
        JOBLENS HEADING
        ================================================== */

        .joblens-welcome {
            font-family: 'Poppins', sans-serif;
            font-size: 52px;
            font-weight: 700;
            line-height: 1.2;
            margin-top: 5px;
            margin-bottom: 25px;
        }

        .joblens-name {
            color: #5A5D66;
        }

        .joblens-ai {
            color: #168FE5;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # INDIA JOB MARKET MOVING BANNER
    # --------------------------------------------------------

    st.html(
        """
        <style>

            .india-banner {
                width: 100%;
                height: 42px;
                overflow: hidden;
                position: relative;

                margin-bottom: 25px;

                border-radius: 10px;

                background: linear-gradient(
                    90deg,
                    #F8FAFC,
                    #EEF6FF,
                    #F8FAFC
                );

                border: 1px solid #D8E3F0;

                display: flex;
                align-items: center;

                box-sizing: border-box;
            }


            .india-banner-text {
                position: absolute;

                white-space: nowrap;

                font-family: 'Poppins', sans-serif;

                font-size: 13px;
                font-weight: 500;

                color: #4B5563;

                left: 0;

                animation: india-scroll 16s linear infinite;
            }


            .india-banner-title {
                color: #1677C8;

                font-weight: 700;

                letter-spacing: 0.6px;
            }


            .india-banner-separator {
                color: #168FE5;

                font-weight: 700;

                margin-left: 12px;
                margin-right: 12px;
            }


            @keyframes india-scroll {

                0% {
                    transform: translateX(-100%);
                }

                100% {
                    transform: translateX(100vw);
                }

            }

        </style>


        <div class="india-banner">

            <div class="india-banner-text">

                <span class="india-banner-title">
                    INDIA JOB MARKET
                </span>

                <span class="india-banner-separator">
                    |
                </span>

                <span>
                    Currently displaying job opportunities across India
                </span>

            </div>

        </div>
        """
    )


    # --------------------------------------------------------
    # WELCOME HEADING
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="joblens-welcome">
            Welcome to
            <span class="joblens-name"> JobLens</span>
            <span class="joblens-ai"> AI</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        Your intelligent companion for navigating the modern job market.

        JobLens AI helps you discover relevant opportunities, understand
        how well your skills match available jobs, and identify skills
        that can strengthen your career profile.
        """
    )

    st.markdown("")

    # --------------------------------------------------------
    # QUICK INTRO
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader("Find Better Opportunities")

        st.write(
            "Search for jobs based on your preferred role, location "
            "and skills. JobLens AI analyzes available opportunities "
            "and highlights jobs that best match your profile."
        )

    st.markdown("")

    # --------------------------------------------------------
    # FEATURED JOBS
    # --------------------------------------------------------

    st.markdown("## Featured Jobs")

    st.caption(
        "Latest 10 job opportunities across all roles and locations."
    )

    featured_jobs = get_featured_jobs()

    if not featured_jobs:

        st.info(
            "No featured jobs are available at the moment."
        )

    else:

        # Display jobs in groups of 2
        for start in range(0, len(featured_jobs), 2):

            job_pair = featured_jobs[start:start + 2]

            cols = st.columns(2)

            for col, job in zip(cols, job_pair):

                with col:

                    with st.container(border=True):

                        st.markdown(
                            f"### {job.get('title', 'Unknown Role')}"
                        )

                        st.write(
                            f"**Company:** "
                            f"{job.get('company_name', job.get('company', 'Unknown'))}"
                        )

                        st.write(
                            f"**Location:** "
                            f"{job.get('location_name', job.get('location', 'Unknown'))}"
                        )

                        if job.get("contract_time"):
                            st.write(
                                f"**Employment:** "
                                f"{job.get('contract_time')}"
                            )

                        st.markdown("")

                        job_url = get_job_url(
                            job.get("job_id")
                        )

                        if not job_url:
                            job_url = job.get("job_url")

                        if job_url:

                            st.link_button(
                                "Apply Now",
                                job_url,
                                type="primary",
                                use_container_width=True
                            )

                        else:

                            st.caption(
                                "Application link unavailable"
                            )

            st.markdown("")
# ============================================================
# JOB SEARCH PAGE
# ============================================================

if st.session_state.page == "Job Search":

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header_col1, header_col2 = st.columns([5, 1])

    with header_col1:
        st.title("Find Your Dream Job")

    with header_col2:
        if st.button(
            "Refresh",
            key="refresh_job_search",
            use_container_width=True
        ):
            # Remember the page currently being viewed
            current_page = st.session_state.get("page", "Job Search")

            # Clear all search/results/form data
            st.session_state.clear()

            # Keep the user on the same page
            st.session_state.page = current_page

            # Reload the application
            st.rerun()

    st.markdown(
        "Find jobs based on your preferred role, location and skills."
    )

    st.divider()


    # --------------------------------------------------------
    # JOB SEARCH FILTERS
    # --------------------------------------------------------

    #st.subheader("Job Search")

    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # JOB ROLE
    # --------------------------------------------------------

    with col1:

        job_role = st.selectbox(
            "Job Role :red[*]",
            JOB_ROLES,
            key="job_role"
        )


    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    with col2:

        location = st.selectbox(
            "Location :red[*]",
            LOCATIONS,
            key="job_location"
        )


    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    st.markdown("### Skills")

    candidate_skills = st.multiselect(
        "Select your skills :red[*]",
        SKILLS,
        placeholder="Select skills",
        key="candidate_skills"
    )


    # --------------------------------------------------------
    # SEARCH BUTTON
    # --------------------------------------------------------

    st.markdown("")

    if st.button(
        "SEARCH JOBS",
        type="primary",
        use_container_width=False
    ):

        if job_role == "Select a role":

            st.warning(
                "Please select a job role."
            )

        elif not candidate_skills:

            st.warning(
                "Please select at least one skill."
            )

        else:

            try:

                response = requests.post(
                    f"{API_URL}/match",
                    json={
                        "skills": candidate_skills,
                        "role": job_role,
                        "location": location,
                        "experience": "Any Experience",
                        "salary": "Any Salary"
                    },
                    timeout=30
                )

                if response.status_code == 200:

                    st.session_state.search_data = (
                        response.json()
                    )

                    st.session_state.show_all_jobs = False

                    st.rerun()

                else:

                    try:
                        error_detail = response.json().get(
                            "detail",
                            "Unknown API error"
                        )
                    except Exception:
                        error_detail = response.text

                    st.error(
                        f"API error "
                        f"{response.status_code}: "
                        f"{error_detail}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to FastAPI. "
                    "Make sure the API is running on "
                    "http://127.0.0.1:8000"
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. "
                    "Please try again."
                )

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )


    # ========================================================
    # SEARCH RESULTS
    # ========================================================

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


        # ----------------------------------------------------
        # SEARCH SUMMARY
        # ----------------------------------------------------

        st.divider()

        recommended_count = len(results)

        st.success(
            f"{jobs_found} jobs found | "
            f"{recommended_count} relevant jobs"
        )


        # ----------------------------------------------------
        # RECOMMENDED JOBS + ANALYTICS BUTTON
        # ----------------------------------------------------

        heading_col, analytics_col = st.columns([5, 1])

        with heading_col:
            st.markdown("## Recommended Jobs")
            st.caption(
                "Top jobs ranked by your skill match."
            )

        with analytics_col:
            if st.button(
                "View Analytics",
                use_container_width=True
            ):
                st.session_state.page = "Analytics"
                st.rerun()


        # ----------------------------------------------------
        # NO RECOMMENDATIONS
        # ----------------------------------------------------

        if not results:

            st.info(
                "No recommended jobs found."
            )


        # ----------------------------------------------------
        # DISPLAY RECOMMENDATIONS
        # ----------------------------------------------------

        else:

            for job in results:
                with st.container(border=True):
                    details_col, action_col = st.columns(
                        [5, 1],
                        vertical_alignment="center"
                    )

                    with details_col:
                        st.markdown(
                            f"### {job.get('title', 'Unknown Role')}"
                        )

                        st.write(
                            f"**Company:** {job.get('company', 'Unknown')}"
                        )

                        st.write(
                            f"**Location:** {job.get('location', 'Unknown')}"
                        )

                        st.write("Resume Match")
                        st.markdown(
                            f"## {job.get('match_score', 0)}%"
                        )

                        matched_skills = job.get("matched_skills", [])
                        missing_skills = job.get("missing_skills", [])

                        if matched_skills:
                            st.write(
                                "**Matched Skills:** "
                                + ", ".join(matched_skills)
                            )

                        if missing_skills:
                            st.write(
                                "**Missing Skills:** "
                                + ", ".join(missing_skills)
                            )

                    with action_col:
                        job_url = get_job_url(job.get("job_id"))

                        if not job_url:
                            job_url = job.get("job_url")

                        if job_url:
                            st.link_button(
                                "Apply Now",
                                job_url,
                                type="primary",
                                use_container_width=True
                            )
                        else:
                            st.caption("Application link unavailable")

                st.markdown("")


        # ----------------------------------------------------
        # EXPLORE ALL JOBS
        # ----------------------------------------------------

        st.markdown(
            "## Explore All Matching Jobs"
        )

        st.write(
            f"**{jobs_found} jobs** are available "
            "for your selected filters."
        )


        # ----------------------------------------------------
        # VIEW ALL BUTTON
        # ----------------------------------------------------

        if not st.session_state.show_all_jobs:

            if st.button(
                "VIEW ALL"
            ):

                st.session_state.show_all_jobs = True

                st.rerun()


        # ----------------------------------------------------
        # ALL JOBS
        # ----------------------------------------------------

        if st.session_state.show_all_jobs:

            st.divider()

            st.subheader(
                f"All Matching Jobs "
                f"({len(all_results)})"
            )

            st.caption(
                "All jobs matching your selected "
                "role and location filters."
            )


            if st.button(
                "← Close"
            ):

                st.session_state.show_all_jobs = False

                st.rerun()


            st.divider()


            if not all_results:

                st.info(
                    "No jobs found for the selected filters."
                )

            else:

                for index, job in enumerate(
                    all_results,
                    start=1
                ):

                    with st.container(border=True):
                        details_col, action_col = st.columns(
                            [5, 1],
                            vertical_alignment="center"
                        )

                        with details_col:
                            st.markdown(
                                f"### {index}. {job.get('title', 'Unknown Role')}"
                            )

                            st.write(
                                f"**Company:** {job.get('company', 'Unknown')}"
                            )

                            st.write(
                                f"**Location:** {job.get('location', 'Unknown')}"
                            )

                            if job.get("skill_data_available", False):
                                st.write("Resume Match")
                                st.markdown(
                                    f"## {job.get('match_score', 0)}%"
                                )

                                matched_skills = job.get("matched_skills", [])
                                missing_skills = job.get("missing_skills", [])

                                if matched_skills:
                                    st.write(
                                        "**Matched Skills:** "
                                        + ", ".join(matched_skills)
                                    )

                                if missing_skills:
                                    st.write(
                                        "**Missing Skills:** "
                                        + ", ".join(missing_skills)
                                    )
                            else:
                                st.info(
                                    "Skill data not available for this job."
                                )

                        with action_col:
                            job_url = get_job_url(job.get("job_id"))

                            if not job_url:
                                job_url = job.get("job_url")

                            if job_url:
                                st.link_button(
                                    "Apply Now",
                                    job_url,
                                    type="primary",
                                    use_container_width=True
                                )
                            else:
                                st.caption("Application link unavailable")

                    st.markdown("")

# ============================================================
# RESUME ANALYSIS PAGE
# ============================================================

elif st.session_state.page == "Resume Analysis":

    st.title("Lets Analyze Your Resume")

    st.markdown(
        "Upload your resume to discover jobs that best match your skills."
    )

    st.divider()

    st.subheader("Upload Your Resume")

    uploaded_resume = st.file_uploader(
        "Choose a PDF resume",
        type=["pdf"],
        help="Upload your latest resume in PDF format."
    )

    if uploaded_resume is not None:

        st.success(
            f"Resume uploaded: {uploaded_resume.name}"
        )

        if st.button("ANALYZE RESUME", type="primary"):

            try:
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as temp_file:
                    temp_file.write(uploaded_resume.getvalue())
                    resume_path = Path(temp_file.name)

                resume_text = extract_text_from_pdf(resume_path)
                resume_data = extract_resume_information(resume_text)
                resume_skills = resume_data.get("skills", [])

                if not resume_skills:
                    st.session_state.resume_data = resume_data
                    st.session_state.resume_jobs = None
                    st.warning(
                        "No supported skills were detected in the resume."
                    )

                else:
                    response = requests.post(
                        f"{API_URL}/match",
                        json={
                            "skills": resume_skills,
                            "role": "All Roles",
                            "location": "All Locations",
                            "experience": "Any Experience",
                            "salary": "Any Salary"
                        },
                        timeout=60
                    )

                    if response.status_code != 200:
                        st.error(
                            f"API error: {response.status_code}"
                        )
                    else:
                        resume_job_data = response.json()

                        st.session_state.resume_data = resume_data
                        st.session_state.resume_jobs = resume_job_data.get(
                            "all_results", []
                        )

                        # Reset UI filters whenever a new resume is analyzed.
                        st.session_state.resume_filter_min_score = "50%+"
                        st.session_state.resume_filter_location = "All Locations"
                        st.session_state.resume_filter_sort = "Match Score ↓"

                        st.rerun()

            except Exception as e:
                st.error(f"Resume analysis failed: {e}")

    # ========================================================
    # ANALYZED RESUME RESULTS
    # ========================================================

    if st.session_state.resume_jobs is not None:

        all_resume_jobs = st.session_state.resume_jobs
        resume_data = st.session_state.resume_data or {}
        resume_skills = resume_data.get("skills", [])

        # ----------------------------------------------------
        # RESUME SKILLS
        # ----------------------------------------------------

        st.subheader("Skills Detected From Your Resume")
        st.write(", ".join(resume_skills))
        st.divider()

        # ----------------------------------------------------
        # RESUME MATCH INSIGHTS
        # ----------------------------------------------------

        st.subheader("Resume Match Insights")

        match_summary = calculate_match_summary(all_resume_jobs)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "🟢 Strong Match",
                match_summary["strong_match"],
                "75%+"
            )

        with col2:
            st.metric(
                "🟡 Moderate Match",
                match_summary["moderate_match"],
                "50–74%"
            )

        with col3:
            st.metric(
                "🔴 Low Match",
                match_summary["low_match"],
                "<50%"
            )

        st.divider()

        # ----------------------------------------------------
        # TOP MISSING SKILLS
        # ----------------------------------------------------

        top_missing_skills = get_top_missing_skills(
            all_resume_jobs,
            top_n=5
        )

        if top_missing_skills:
            with st.container(border=True):
                st.subheader("Top Missing Skills")
                st.caption(
                    "Skills frequently requested by relevant jobs "
                    "that are not detected in your resume."
                )

                for index, item in enumerate(top_missing_skills, start=1):
                    st.markdown(
                        f"**{index}. {item['skill']}** — requested by "
                        f"{item['job_count']} relevant jobs"
                    )

        st.divider()

        # ----------------------------------------------------
        # JOB FILTERS
        # ----------------------------------------------------

        st.subheader("Jobs Based on Your Resume")
        st.caption("Filter and sort jobs using your resume match score.")

        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:
            min_score_label = st.selectbox(
                "Minimum Match Score",
                ["50%+", "60%+", "70%+", "80%+", "90%+"],
                key="resume_filter_min_score"
            )

        with filter_col2:
            # Build locations from the actual analyzed jobs.
            location_values = []
            for job in all_resume_jobs:
                value = str(job.get("location", "")).strip()
                if value and value not in location_values:
                    location_values.append(value)

            location_options = ["All Locations"] + sorted(location_values)

            current_location = st.session_state.resume_filter_location
            if current_location not in location_options:
                st.session_state.resume_filter_location = "All Locations"

            selected_location = st.selectbox(
                "Location",
                location_options,
                key="resume_filter_location"
            )

        with filter_col3:
            sort_option = st.selectbox(
                "Sort By",
                ["Match Score ↓", "Match Score ↑", "Job Title A–Z"],
                key="resume_filter_sort"
            )

        # ----------------------------------------------------
        # APPLY FILTERS DIRECTLY
        # ----------------------------------------------------

        min_score = int(min_score_label.replace("%+", ""))

        filtered_resume_jobs = []

        for job in all_resume_jobs:
            try:
                score = float(job.get("match_score", 0) or 0)
            except (TypeError, ValueError):
                score = 0

            if score < min_score:
                continue

            if selected_location != "All Locations":
                job_location = str(job.get("location", "")).strip()
                if job_location != selected_location:
                    continue

            filtered_resume_jobs.append(job)

        if sort_option == "Match Score ↓":
            filtered_resume_jobs.sort(
                key=lambda job: float(job.get("match_score", 0) or 0),
                reverse=True
            )
        elif sort_option == "Match Score ↑":
            filtered_resume_jobs.sort(
                key=lambda job: float(job.get("match_score", 0) or 0)
            )
        else:
            filtered_resume_jobs.sort(
                key=lambda job: str(job.get("title", "")).lower()
            )

        st.success(f"{len(filtered_resume_jobs)} jobs found")

        # ----------------------------------------------------
        # FILTERED JOB CARDS
        # ----------------------------------------------------

        if not filtered_resume_jobs:
            st.info("No jobs match the selected filters.")

        else:
            for job in filtered_resume_jobs:
                with st.container(border=True):
                    details_col, action_col = st.columns(
                        [5, 1],
                        vertical_alignment="center"
                    )

                    with details_col:
                        st.markdown(
                            f"### {job.get('title', 'Unknown Role')}"
                        )

                        st.write(
                            f"**Company:** {job.get('company', 'Unknown')}"
                        )

                        st.write(
                            f"**Location:** {job.get('location', 'Unknown')}"
                        )

                        st.write("Resume Match")
                        st.markdown(
                            f"## {job.get('match_score', 0)}%"
                        )

                        matched_skills = job.get("matched_skills", [])
                        missing_skills = job.get("missing_skills", [])

                        if matched_skills:
                            st.write(
                                "**Matched Skills:** "
                                + ", ".join(matched_skills)
                            )

                        if missing_skills:
                            st.write(
                                "**Skills to Develop:** "
                                + ", ".join(missing_skills)
                            )

                    with action_col:
                        job_url = get_job_url(job.get("job_id"))

                        if job_url:
                            st.link_button(
                                "Apply Now",
                                job_url,
                                type="primary",
                                use_container_width=True
                            )
                        else:
                            st.caption("Application link unavailable")

                st.markdown("")

# ============================================================
# ANALYTICS PAGE
# ============================================================

elif st.session_state.page == "Analytics":

    if st.button("← Back"):
        st.session_state.page = "Job Search"
        st.rerun()

    st.title("Job Market Analytics")

    st.markdown(
        "Explore insights from the jobs returned by your "
        "current job search."
    )

    st.divider()

    # --------------------------------------------------------
    # GET AVAILABLE JOB DATA
    # --------------------------------------------------------

    analytics_jobs = []

    if st.session_state.search_data:
        analytics_jobs = st.session_state.search_data.get(
            "all_results",
            []
        )

    # --------------------------------------------------------
    # NO DATA
    # --------------------------------------------------------

    if not analytics_jobs:
        st.info("No job data is available yet.")
        st.markdown(
            "Go to **Job Search**, perform a search, "
            "and then return here to view analytics."
        )

    else:

         # ----------------------------------------------------
        # ANALYTICS CALCULATIONS
        # ----------------------------------------------------

        total_jobs = get_total_jobs(
            analytics_jobs
        )

        average_match = get_average_match_score(
            analytics_jobs
        )

        locations = get_jobs_by_location(
            analytics_jobs
        )

        roles = get_jobs_by_role(
            analytics_jobs
        )

        top_skills = get_top_skills(
            analytics_jobs,
            top_n=10
        )

        match_distribution = get_match_score_distribution(
            analytics_jobs
        )

        # ----------------------------------------------------
        # KPI CARDS
        # ----------------------------------------------------

        st.subheader("Job Market Overview")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Jobs",
                total_jobs
            )

        with col2:

            st.metric(
                "Average Match Score",
                f"{average_match:.0f}%"
            )

        with col3:

            st.metric(
                "Locations",
                len(locations)
            )

        st.markdown("")

        # ----------------------------------------------------
        # JOBS BY ROLE + LOCATION — CARD UI
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            with st.container(border=True):

                st.subheader("Jobs by Role")

                if roles:

                    st.bar_chart(
                        roles
                    )

                else:

                    st.info(
                        "No role data available."
                    )

        with col2:

            with st.container(border=True):

                st.subheader("Jobs by Location")

                if locations:

                    st.bar_chart(
                        locations
                    )

                else:

                    st.info(
                        "No location data available."
                    )

        st.markdown("")

        # ----------------------------------------------------
        # TOP SKILLS — CARD UI
        # ----------------------------------------------------

        with st.container(border=True):

            st.subheader(
                "Most Demanded Skills"
            )

            if top_skills:

                skill_data = {
                    skill.title(): count
                    for skill, count in top_skills
                }

                st.bar_chart(
                    skill_data
                )

            else:

                st.info(
                    "Skill data is not available for these jobs."
                )

        st.markdown("")

        # ----------------------------------------------------
        # MATCH SCORE DISTRIBUTION — CARD UI
        # ----------------------------------------------------

        with st.container(border=True):

            st.subheader(
                "Resume Match Score Distribution"
            )

            st.bar_chart(
                match_distribution
            )

        st.markdown("")

        # ----------------------------------------------------
        # ANALYTICS NOTE
        # ----------------------------------------------------

        st.caption(
            "Analytics are calculated from the jobs returned "
            "by your current search. Jobs without skill data "
            "are excluded from match-score calculations."
        )



# ============================================================
# PRIVACY POLICY PAGE
# ============================================================

if st.session_state.page == "Privacy":

    st.title("Privacy Policy")

    st.markdown(
        """
        **Last Updated: August 31, 2026**

        Welcome to **JobLens AI**, an AI-powered job market analytics
        platform. Your privacy is important to us. This Privacy Policy
        explains how information is handled when you use our platform.

        ### 1. Information We Collect

        Depending on the features you use, JobLens AI may process:

        - Job search preferences such as role, location, and skills.
        - Resume files or resume information submitted for analysis.
        - Information required to generate job market insights and
          recommendations.
        - Basic technical information required for the application to
          function properly.

        We only use information that is necessary to provide and improve
        the features of the platform.

        ### 2. How We Use Your Information

        Information provided to JobLens AI may be used to:

        - Provide job search and job market analytics.
        - Analyze resumes and provide relevant insights.
        - Generate job recommendations and career-related insights.
        - Improve application functionality and user experience.
        - Maintain the security and reliability of the platform.

        ### 3. Resume Privacy

        If you upload a resume for analysis, the contents of the resume
        may be processed to generate the requested analysis.

        Users should avoid uploading sensitive personal information that
        is not necessary for resume analysis.

        ### 4. Data Security

        We take reasonable measures to protect information processed
        through JobLens AI against unauthorized access, alteration,
        disclosure, or destruction.

        However, no internet-based application can guarantee absolute
        security of information.

        ### 5. Third-Party Services

        JobLens AI may use third-party services, APIs, cloud services,
        or data providers to provide certain application functionality.

        Information processed by such services may be subject to their
        respective privacy policies and terms of service.

        ### 6. Data Retention

        Information should only be retained for as long as reasonably
        necessary to provide the requested functionality, maintain the
        application, comply with applicable requirements, or resolve
        disputes.

        ### 7. Your Responsibility

        You are responsible for ensuring that the information you provide
        to JobLens AI is accurate and that you have the necessary rights
        to submit any documents or information you upload.

        ### 8. Children's Privacy

        JobLens AI is not intended to knowingly collect personal
        information from children.

        ### 9. Changes to This Privacy Policy

        This Privacy Policy may be updated from time to time to reflect
        changes in the application, technology, or applicable requirements.

        Any updated version will be made available through the platform.

        ### 10. Contact Us

        If you have questions, concerns, or requests regarding this
        Privacy Policy or the handling of information, please contact
        the JobLens AI project team through the appropriate project
        contact channel.

        ---

        **JobLens AI**  
        *AI-Powered Job Market Analytics Platform*
        """
    )
    
# ============================================================
# CONTACT US PAGE
# ============================================================

if st.session_state.page == "Contact Us":

    st.title("Contact Us")

    st.markdown(
        "We’re here to help you make the most of JobLens AI. "
        "If you have any questions, feedback, suggestions, or need assistance, "
        "feel free to get in touch with our team."
    )

    st.divider()

    st.subheader("Get in Touch")

    st.markdown(
        """
        **Have a question or feedback?**

        We value your feedback and are always looking for ways to improve
        JobLens AI. Whether you have encountered an issue, have a suggestion
        for a new feature, or simply want to learn more about the platform,
        we'd be happy to hear from you.

        **Email:** support@joblensai.com

        **Response Time:**  
        Our team aims to respond to all queries within 2–3 business days.
        """
    )

    st.info(
        "For technical issues, please include a brief description of the "
        "problem and any relevant details so we can assist you more effectively."
    )

    st.markdown(
        """
        ### Thank You

        Thank you for using **JobLens AI**. Your feedback helps us build a
        smarter and more useful job-market analytics platform.
        """
    )
    
# ============================================================
# APP FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        margin-top: 60px;
        padding: 22px 10px 12px 10px;
        border-top: 1px solid rgba(128, 128, 128, 0.25);
        text-align: center;
        opacity: 0.65;
        font-size: 13px;
    ">
        All rights reserved © 2026 JobLens AI.
    </div>
    """,
    unsafe_allow_html=True
)