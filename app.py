import streamlit as st

from parser import extract_text
from grok_ranker import rank_resumes

st.set_page_config(
    page_title="AI-Powered ATS",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 AI-Powered Applicant Tracking System (ATS)")
st.write(
    "Upload PDF or DOCX resumes and rank candidates using Gemini AI."
)
# ------------------------------
# Sidebar Weightages
# -----------------------------

st.sidebar.header("Evaluation Weightages")

skills_weight = st.sidebar.slider(
    "Skills Match (%)",
    0,
    100,
    50
)

experience_weight = st.sidebar.slider(
    "Experience (%)",
    0,
    100,
    20
)

projects_weight = st.sidebar.slider(
    "Projects (%)",
    0,
    100,
    15
)

education_weight = st.sidebar.slider(
    "Education (%)",
    0,
    100,
    10
)

certification_weight = st.sidebar.slider(
    "Certifications (%)",
    0,
    100,
    5
)

# -----------------------------
# Job Description
# -----------------------------

job_desc = st.text_area(
    "Paste Job Description",
    height=250
)

# -----------------------------
# Resume Upload
# -----------------------------

uploaded_files = st.file_uploader(
    "Upload Resumes (PDF or DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# -----------------------------
# Rank Button
# -----------------------------

if st.button("Rank Resumes"):

    if not job_desc:
        st.error("Please enter a Job Description.")
        st.stop()

    if not uploaded_files:
        st.error("Please upload resumes.")
        st.stop()

    progress = st.progress(0)

    with st.spinner("Analyzing resumes using Gemini AI..."):

        resumes = []

        progress.progress(20)

        for file in uploaded_files:

            try:

                resume_text = extract_text(file)

                resumes.append(
                    {
                        "filename": file.name,
                        "content": resume_text
                    }
                )

            except Exception as e:
                st.error(
                    f"Error reading {file.name}: {e}"
                )

        progress.progress(50)

        try:

            result = rank_resumes(
                job_desc=job_desc,
                resumes=resumes,
                skills_weight=skills_weight,
                experience_weight=experience_weight,
                projects_weight=projects_weight,
                education_weight=education_weight,
                certification_weight=certification_weight
            )

            progress.progress(100)

            st.success("Ranking Completed!")

            # -----------------------------
            # Evaluation Criteria
            # -----------------------------

            st.subheader("Evaluation Criteria Used")

            st.write(
                f"Skills Match: {skills_weight}%"
            )

            st.write(
                f"Experience: {experience_weight}%"
            )

            st.write(
                f"Projects: {projects_weight}%"
            )

            st.write(
                f"Education: {education_weight}%"
            )

            st.write(
                f"Certifications: {certification_weight}%"
            )

            st.markdown("---")

            st.subheader("🏆 Top 3 Candidates")

            # -----------------------------
            # Candidate Results
            # -----------------------------

            for candidate in result["top_3"]:

                st.markdown("---")

                st.markdown(
                    f"## Rank #{candidate.get('rank')}"
                )

                st.write(
                    f"**Resume:** {candidate.get('resume')}"
                )

                st.write(
                    f"**ATS Match Score:** {candidate.get('score')}%"
                )

                st.write(
                    f"**Recommendation:** {candidate.get('recommendation', 'N/A')}"
                )

                st.write(
                    f"**Reason:** {candidate.get('reason', 'N/A')}"
                )

                st.write(
                    f"**Matched Skills:** {', '.join(candidate.get('matched_skills', []))}"
                )

                st.write(
                    f"**Missing Skills:** {', '.join(candidate.get('missing_skills', []))}"
                )

                st.write(
                    f"**Strengths:** {', '.join(candidate.get('strengths', []))}"
                )

            st.markdown("---")

            with st.expander(
                "View Full Gemini Response"
            ):
                st.json(result)

            

        except Exception as e:

            st.error(
                f"Error: {str(e)}"
            )

