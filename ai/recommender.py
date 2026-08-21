from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import os

load_dotenv()

# --------------------------------------------------
# RESPONSE STRUCTURE
# --------------------------------------------------

class PolicyRecommendation(BaseModel):

    project_title: str = Field(
        description="Name of the recommended development project"
    )

    priority: str = Field(
        description="Priority level: Low, Medium, High, or Critical"
    )

    reason: str = Field(
        description="Why this project should be prioritized"
    )

    recommended_action: str = Field(
        description="Specific government intervention recommended"
    )

    expected_impact: str = Field(
        description="Expected positive impact of the project"
    )

    key_beneficiaries: str = Field(
        description="Main groups of citizens who would benefit"
    )

    implementation_notes: str = Field(
        description="Practical implementation considerations"
    )


# --------------------------------------------------
# GEMINI POLICY RECOMMENDATION
# --------------------------------------------------

def generate_policy_recommendation(data):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured."
        )

    # Create Gemini client exactly like extractor.py
    client = genai.Client(
        api_key=api_key
    )


    # --------------------------------------------------
    # PROMPT
    # --------------------------------------------------

    prompt = f"""
You are JanDrishti AI, an Indian public
infrastructure policy intelligence system.

Analyze the following citizen-demand hotspot.

HOTSPOT INFORMATION:

State:
{data.get("state")}

District:
{data.get("district")}

Top Problem:
{data.get("category")}

Citizen Requests:
{data.get("requests")}

Population Affected:
{data.get("population_affected")}

Average Severity:
{data.get("avg_severity")}

Infrastructure Gap:
{data.get("infrastructure_gap")}%

Development Gap:
{data.get("development_gap")}%

Priority Score:
{data.get("priority_score")}/100


Your task is to recommend a practical
government development intervention.

Consider:

1. Citizen demand
2. Population impact
3. Severity
4. Infrastructure gap
5. Development gap

IMPORTANT RULES:

- Do NOT invent statistics.
- Only use the information provided.
- Do not claim that a government project already exists.
- Give a practical infrastructure intervention.
- Keep the recommendation realistic for an Indian
  government or local authority.
- Explain why the area deserves attention.
- The priority should reflect the provided
  priority score.


Return the result as structured JSON.
"""


    # --------------------------------------------------
    # GEMINI REQUEST
    # --------------------------------------------------

    response = client.models.generate_content(

        model="gemini-3.6-flash",

        contents=prompt,

        config=types.GenerateContentConfig(

            response_mime_type="application/json",

            response_schema=(
                PolicyRecommendation
                .model_json_schema()
            )
        )
    )


    # --------------------------------------------------
    # VALIDATE RESPONSE
    # --------------------------------------------------

    return PolicyRecommendation.model_validate_json(
        response.text
    )