import streamlit as st
import json

from parser import extract_text
from grok_ranker import rank_resumes

st.set_page_config(
    page_title="AI-Powered ATS",
    page_icon="🏆",
    layout="wide"
)

# ==================================================
# Header
# ==================================================

st.title("🏆 AI-Powered Applicant Tracking System (ATS)")
st.markdown(
    """
Upload PDF or DOCX resumes and rank candidates using Gemini AI.

The ATS evaluates candidates based on:
- Skills Match
- Experience
- Projects
- Education
- Certifications
"""
)

# ==================================================
# Sidebar
# ==================================================

st.sidebar.header("⚙️ Evaluation Weightages")

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

# ==================================================
# Job Description
# ==================================================

st.subheader("📋 Job Description")

job_desc = st.text_area(
    "Paste the Job Description",
    height=250
)

# ==================================================
# Resume Upload
# ==================================================

st.subheader("📁 Upload Resumes")

uploaded_files = st.file_uploader(
    "Upload PDF or DOCX Resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True
)
# ==================================================
# Shortlisting Settings
# ==================================================

st.subheader("🎯 Shortlisting Settings")

shortlist_count = st.number_input(
    "Number of Candidates to Shortlist",
    min_value=1,
    max_value=100,
    value=3,
    step=1
)

minimum_score = st.slider(
    "Minimum ATS Score Required",
    min_value=0,
    max_value=100,
    value=60
)
# ==================================================
# Rank Button
# ==================================================

if st.button("🚀 Rank Resumes"):

    if not job_desc:
        st.error("Please enter a Job Description.")
        st.stop()

    if not uploaded_files:
        st.error("Please upload at least one resume.")
        st.stop()

    progress = st.progress(0)

    with st.spinner(
        "🔍 Extracting resumes | 🧠 Matching skills | 📊 Ranking candidates..."
    ):

        resumes = []

        progress.progress(20)

        # ------------------------------------------
        # Extract Resume Content
        # ------------------------------------------

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

        # ------------------------------------------
        # ATS Ranking
        # ------------------------------------------

        try:

            result = rank_resumes(
            job_desc=job_desc,
            resumes=resumes,
            skills_weight=skills_weight,
            experience_weight=experience_weight,
            projects_weight=projects_weight,
            education_weight=education_weight,
            certification_weight=certification_weight,
            shortlist_count=shortlist_count,
            minimum_score=minimum_score
        )
            progress.progress(100)

            st.success("✅ Ranking Completed Successfully!")

            # ==========================================
            # Dashboard Metrics
            # ==========================================

            top_score = max(
                candidate["score"]
                for candidate in result["top_candidates"]
            )

            best_candidate = result["top_candidates"][0]

            st.success(
                f"🥇 Best Candidate: "
                f"{best_candidate['resume']} "
                f"| Score: {best_candidate['score']}%"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "📄 Resumes Uploaded",
                    len(uploaded_files)
                )

            with col2:
                st.metric(
                    "🏆 Candidates Ranked",
                    len(result["top_candidates"])
                )

            with col3:
                st.metric(
                    "⭐ Highest Score",
                    f"{top_score}%"
                )

            st.markdown("---")

            # ==========================================
            # Evaluation Criteria
            # ==========================================

            st.subheader("⚙️ Evaluation Criteria Used")

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric(
                "Skills",
                f"{skills_weight}%"
            )

            col2.metric(
                "Experience",
                f"{experience_weight}%"
            )

            col3.metric(
                "Projects",
                f"{projects_weight}%"
            )

            col4.metric(
                "Education",
                f"{education_weight}%"
            )

            col5.metric(
                "Certification",
                f"{certification_weight}%"
            )

            st.markdown("---")

            # ==========================================
            # Top Ranked Candidates
            # ==========================================

            st.subheader(
            f"🏆 Top {shortlist_count} Shortlisted Candidates"
            )

            st.caption(
                "Detailed ATS analysis for the highest-ranked candidates."
            )

            for candidate in result["top_candidates"]:

                rank = candidate.get("rank")
                score = candidate.get("score", 0)

                with st.expander(
                    f"🏆 Rank #{rank} - {candidate.get('resume')}",
                    expanded=(rank == 1)
                ):

                    st.progress(score / 100)

                    st.markdown(
                        f"### ATS Match Score: {score}%"
                    )

                    recommendation = candidate.get(
                        "recommendation",
                        "N/A"
                    )

                    if recommendation == "Highly Recommended":
                        st.success(recommendation)

                    elif recommendation == "Recommended":
                        st.info(recommendation)

                    elif recommendation == "Consider":
                        st.warning(recommendation)

                    else:
                        st.error(recommendation)

                    st.write(
                        f"**Reason:** {candidate.get('reason', 'N/A')}"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.markdown(
                            "### ✅ Matched Skills"
                        )

                        matched_skills = candidate.get(
                            "matched_skills",
                            []
                        )

                        if matched_skills:

                            for skill in matched_skills:
                                st.write(f"• {skill}")

                        else:
                            st.write("None")

                    with col2:

                        st.markdown(
                            "### ❌ Missing Skills"
                        )

                        missing_skills = candidate.get(
                            "missing_skills",
                            []
                        )

                        if missing_skills:

                            for skill in missing_skills:
                                st.write(f"• {skill}")

                        else:
                            st.write("None")

                    st.markdown(
                        "### 💪 Strengths"
                    )

                    strengths = candidate.get(
                        "strengths",
                        []
                    )

                    if strengths:

                        for strength in strengths:
                            st.write(
                                f"• {strength}"
                            )

                    else:
                        st.write("No strengths provided.")

            st.markdown("---")

            # ==========================================
            # Download Results
            # ==========================================

            st.download_button(
                label="📥 Download ATS Results",
                data=json.dumps(
                    result,
                    indent=4
                ),
                file_name="ats_results.json",
                mime="application/json"
            )

            # ==========================================
            # Raw Gemini Output
            # ==========================================

            with st.expander(
                "🔍 View Full Gemini Response"
            ):
                st.json(result)

        except Exception as e:

            st.error(
                f"Error: {str(e)}"
            )
