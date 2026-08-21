from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Literal
import os


class CitizenRequest(BaseModel):

    language: str = Field(
        description="Language used by the citizen"
    )

    category: Literal[
        "Roads",
        "Water",
        "Healthcare",
        "Education",
        "Electricity",
        "Sanitation",
        "Public Transport",
        "Internet Connectivity",
        "Agriculture",
        "Housing",
        "Other"
    ]

    problem: str = Field(
        description="Short description of the infrastructure problem"
    )

    location: str = Field(
        description="Location mentioned by the citizen. Return 'Unknown' if absent."
    )

    severity: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    urgency: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    affected_service: str = Field(
        description="Public service affected by the problem"
    )

    affected_population_estimate: int = Field(
        description="Estimated number of people affected if possible, otherwise 0"
    )

    summary: str = Field(
        description="One sentence summary of the citizen's request"
    )


def analyze_request(text: str) -> CitizenRequest:

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(
        api_key=api_key
    )

    prompt = f"""
You are JanDrishti AI, an Indian public infrastructure
intelligence system.

Analyze the citizen's development request.

The citizen may write in Hindi, Marathi, English,
or another Indian language.

Do NOT invent information.

If location is not explicitly available,
return "Unknown".

If affected population cannot be estimated
from the request, return 0.

Classify the request into the closest
available category.

Citizen request:

{text}
"""

    response = client.models.generate_content(

        model="gemini-3.6-flash",

        contents=prompt,

        config=types.GenerateContentConfig(

            response_mime_type="application/json",

            response_schema=
                CitizenRequest.model_json_schema()
        )
    )

    return CitizenRequest.model_validate_json(
        response.text
    )