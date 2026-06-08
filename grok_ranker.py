import os
import json
import re
import streamlit as st

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")


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
    certification_weight,
    shortlist_count,
    minimum_score
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
6. Return EXACTLY the Top {shortlist_count}
highest-ranked candidates.

7. Exclude candidates scoring below
{minimum_score}.

8. If fewer candidates qualify,
return only those candidates.
9. Mention strengths.
10. Mention matched skills.
11. Mention missing skills.
12. Provide recommendation: if required or NA
13. ONLY compare candidates against skills, qualifications, and requirements explicitly mentioned in the Job Description.
14. NEVER invent additional skills, technologies, certifications, or requirements.
15. A skill can be listed in "missing_skills" ONLY if it is explicitly present in the Job Description.
16. If a skill is not mentioned in the Job Description, do not include it in matched_skills or missing_skills.
17. Do not assume industry-standard requirements.

Return ONLY valid JSON.

JSON FORMAT:

{{
  "top_candidates": [
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

