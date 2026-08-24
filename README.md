# JanDrishti AI

## AI-Powered Citizen & Policy Intelligence Platform

JanDrishti AI is an intelligent civic platform designed to connect citizens, government data, and policy decision-making through AI-powered analysis.

The platform provides two major interfaces:

- **Citizen Portal** – Allows citizens to submit issues and interact with the system using natural language and voice.
- **Policy Portal** – Provides administrators and policymakers with analytics, development indicators, hotspots, priorities, and recommendations.

---

## Key Features

### Citizen Portal

- Natural language complaint/request processing
- AI-powered request extraction
- Location detection and geocoding
- Issue categorization
- Citizen-friendly responses
- Voice-based interaction
- Request storage in database

### Policy Portal

- District-level development analysis
- Infrastructure analysis
- Development indicators
- Issue analytics
- Hotspot identification
- Priority analysis
- AI-powered recommendations
- National-level infrastructure insights

---

## Technology Stack

### Frontend

- Streamlit

### Backend

- Python
- SQLite

### AI / Machine Learning

- Google Gemini API
- Scikit-learn
- Natural Language Processing

### Data Processing

- Pandas
- NumPy

### Location Services

- Geopy
- Geocoding APIs

### Visualization

- Plotly
- Folium
- Streamlit-Folium

---

## Project Structure

```text
jandrishthi-ai/
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── app.py
│
├── ai/
│   ├── extractor.py
│   ├── recommender.py
│   └── voice.py
│
├── data/
│   ├── national_infrastructure.csv

│
├── database/
│   ├── database.py
│   └── jandrishthi.db
│
├── pages/
│   ├── citizen_portal.py
│   └── policy_portal.py
│
└── utils/
    ├── __init__.py
    ├── analytics.py
    ├── development.py
    ├── districts.py
    ├── geocoding.py
    ├── hotspots.py
    ├── national_data.py
    └── priority.py
