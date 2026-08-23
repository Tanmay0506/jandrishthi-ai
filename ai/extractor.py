import os

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class ComplaintAnalysis(BaseModel):
    category: str = Field(
        description="Infrastructure issue category, for example Roads or Water Supply."
    )
    severity: str = Field(
        description="Low, Medium, High, or Critical."
    )
    urgency: str = Field(
        description="Routine, Soon, Urgent, or Immediate."
    )
    affected_population_estimate: int = Field(
        description="Estimated number of people affected."
    )
    language: str = Field(
        description="Language used by the citizen."
    )
    problem: str = Field(
        description="The main infrastructure problem."
    )
    affected_service: str = Field(
        description="Public service or infrastructure affected."
    )
    summary: str = Field(
        description="Short, clear summary of the complaint."
    )
    location: str = Field(
        description="Specific locality, city, district, or state mentioned. Use Unknown only when absent."
    )


def analyze_request(request_text: str) -> ComplaintAnalysis:
    """
    Convert a citizen complaint into structured JanDrishti intelligence.
    No audio recording logic belongs in this file.
    """
    if not request_text or not request_text.strip():
        raise ValueError("Complaint text cannot be empty.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add it to your .env file or Render environment variables."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are JanDrishti AI, an Indian civic infrastructure complaint analyst.

Analyze this citizen complaint and return only structured data matching the required schema.

Complaint:
{request_text}

Rules:
- Identify the most relevant infrastructure category.
- Severity must be one of: Low, Medium, High, Critical.
- Urgency must be one of: Routine, Soon, Urgent, Immediate.
- Estimate affected population conservatively as an integer.
- Preserve the complaint language.
- Extract the most specific location mentioned.
- If no location is present, return "Unknown".
- Do not invent addresses, villages, districts, or states.
"""

    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ComplaintAnalysis,
                temperature=0.2,
            ),
        )

        if response.parsed:
            return response.parsed

        return ComplaintAnalysis.model_validate_json(response.text)

    except Exception as error:
        raise RuntimeError(f"AI analysis failed: {error}") from error
