import os
import json
import re
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Get API Key from .env (local) or Streamlit Secrets (cloud)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    api_key = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

def rank_resumes(
    job_desc,
    resumes,
    skills_weight,
    experience_weight,
    projects_weight,
    education_weight,
    certification_weight
):

    resumes_text = ""

    for resume in resumes:

        resumes_text += f"""

Resume: {resume['filename']}

{resume['content']}

=====================================

"""

    prompt = f"""
You are an AI-powered Applicant Tracking System (ATS)
and Senior Technical Recruiter.

JOB DESCRIPTION:

{job_desc}

Evaluation Weightages:

Skills Match = {skills_weight}%
Experience = {experience_weight}%
Projects = {projects_weight}%
Education = {education_weight}%
Certifications = {certification_weight}%

Instructions:

1. Compare all candidates against the Job Description.
2. Use the above weightages exactly.
3. Infer skills from education and experience.
4. Do NOT mark inferred skills as missing.
5. Rank candidates relative to each other.
6.If 3 or more resumes are uploaded, return EXACTLY the Top 3 highest-ranked candidates.
7. If fewer than 3 resumes are uploaded, return all available candidates.
8. Give score out of 100.
9. Mention strengths.
10. Mention matched skills.
11. Mention missing skills.
12. Provide recommendation: if required or NA

Return ONLY valid JSON.

JSON FORMAT:

{{
  "top_3": [
    {{
      "rank": 1,
      "resume": "candidate1.pdf or DOCX",
      "score": 95,
      "matched_skills": ["Python", "SQL"],
      "missing_skills": ["AWS"],
      "strengths": [
        "Strong Python experience",
        "REST API expertise"
      ],
      "recommendation": "Highly Recommended",
      "reason": "Excellent match with the job requirements"
    }},
    {{
      "rank": 2,
      "resume": "candidate2.pdf or .DOCX",
      "score": 90,
      "matched_skills": ["Python", "Git"],
      "missing_skills": ["AWS"],
      "strengths": [
        "Good project portfolio"
      ],
      "recommendation": "Recommended",
      "reason": "Good technical match"
    }},
    {{
      "rank": 3,
      "resume": "candidate3.pdf or .DOCX",
      "score": 85,
      "matched_skills": ["Python"],
      "missing_skills": ["AWS"],
      "strengths": [
        "Relevant academic background"
      ],
      "recommendation": "Consider",
      "reason": "Moderate match"
    }}
  ]
}}

RESUMES:

{resumes_text}
"""

    response = model.generate_content(prompt)

    content = response.text

    match = re.search(
        r'\{{.*\}}',
        content,
        re.DOTALL
    )

    if not match:

        match = re.search(
            r'\{.*\}',
            content,
            re.DOTALL
        )

    if not match:
        raise Exception(
            f"Gemini returned invalid JSON:\n\n{content}"
        )

    return json.loads(
        match.group()
    )

