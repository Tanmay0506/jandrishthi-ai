import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).parent / "jandrishthi.db"


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


# ==================================================
# CREATE TABLES
# ==================================================

def create_table():

    connection = get_connection()
    cursor = connection.cursor()

    # ----------------------------------------------
    # CITIZEN REQUESTS
    # ----------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citizen_requests (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        language TEXT,
        category TEXT,
        problem TEXT,
        location TEXT,

        latitude REAL,
        longitude REAL,
        village TEXT,
        district TEXT,
        state TEXT,

        severity TEXT,
        urgency TEXT,
        affected_service TEXT,
        affected_population INTEGER,
        summary TEXT,
        original_text TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ----------------------------------------------
    # POLICY RECOMMENDATIONS
    # ----------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS policy_recommendations (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        state TEXT NOT NULL,
        district TEXT NOT NULL,
        category TEXT NOT NULL,

        priority_score REAL,

        project_title TEXT,
        priority TEXT,

        reason TEXT,
        recommended_action TEXT,

        expected_impact TEXT,

        key_beneficiaries TEXT,

        implementation_notes TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        UNIQUE (
            state,
            district,
            category
        )
    )
    """)

    connection.commit()
    connection.close()


# ==================================================
# SAVE CITIZEN REQUEST
# ==================================================

def save_request(
    request,
    original_text,
    location_data
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO citizen_requests (

            language,
            category,
            problem,
            location,

            latitude,
            longitude,
            village,
            district,
            state,

            severity,
            urgency,
            affected_service,
            affected_population,
            summary,
            original_text
        )

        VALUES (
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?
        )
    """, (

        request.language,
        request.category,
        request.problem,

        location_data.get(
            "input_location",
            ""
        ),

        location_data.get("latitude"),
        location_data.get("longitude"),
        location_data.get("village"),
        location_data.get("district"),
        location_data.get("state"),

        request.severity,
        request.urgency,
        request.affected_service,

        request.affected_population_estimate,

        request.summary,
        original_text
    ))

    connection.commit()
    connection.close()


# ==================================================
# SAVE POLICY RECOMMENDATION
# ==================================================

def save_policy_recommendation(
    data,
    recommendation
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO policy_recommendations (

            state,
            district,
            category,

            priority_score,

            project_title,
            priority,

            reason,
            recommended_action,

            expected_impact,

            key_beneficiaries,

            implementation_notes
        )

        VALUES (
            ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?, ?
        )
    """, (

        data.get("state"),
        data.get("district"),
        data.get("category"),

        data.get("priority_score"),

        recommendation.project_title,
        recommendation.priority,

        recommendation.reason,
        recommendation.recommended_action,

        recommendation.expected_impact,

        recommendation.key_beneficiaries,

        recommendation.implementation_notes
    ))

    connection.commit()
    connection.close()


# ==================================================
# GET POLICY RECOMMENDATION
# ==================================================

def get_policy_recommendation(
    state,
    district,
    category
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT

            project_title,
            priority,
            reason,
            recommended_action,
            expected_impact,
            key_beneficiaries,
            implementation_notes

        FROM policy_recommendations

        WHERE state = ?
        AND district = ?
        AND category = ?

        LIMIT 1
    """, (

        state,
        district,
        category
    ))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {

        "project_title": row[0],
        "priority": row[1],
        "reason": row[2],
        "recommended_action": row[3],
        "expected_impact": row[4],
        "key_beneficiaries": row[5],
        "implementation_notes": row[6]
    }