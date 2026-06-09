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
    "gemini-2.5-flash-lite"
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

{resume['content'][:4000]}

=====================================

"""

    prompt = f"""
Act as an ATS recruiter.

Job Description:
{job_desc}

Weights:
Skills={skills_weight}
Experience={experience_weight}
Projects={projects_weight}
Education={education_weight}
Certifications={certification_weight}

Rules:
- Rank candidates against the JD.
- Return top {shortlist_count} candidates.
- Exclude scores below {minimum_score}.
- Only use requirements explicitly mentioned in the JD.
- Do not invent skills.
- Infer skills from experience if clearly evident.

Return ONLY JSON:

{{
  "top_candidates":[
    {{
      "rank":1,
      "resume":"",
      "score":0,
      "matched_skills":[],
      "missing_skills":[],
      "strengths":[],
      "recommendation":"",
      "reason":""
    }}
  ]
}}

Resumes:

{resumes_text}
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.1
        }
    )
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

