import pandas as pd

from utils.national_data import (
    get_district_data
)


# ==================================================
# PRIORITY ENGINE
# ==================================================

def calculate_priority(df):

    df = df.copy()


    # ------------------------------------------------
    # SEVERITY SCORE
    # ------------------------------------------------

    severity_map = {

        "Low": 25,

        "Medium": 50,

        "High": 75,

        "Critical": 100
    }


    df["severity_score"] = (
        df["severity"]
        .map(severity_map)
        .fillna(25)
    )


    # ------------------------------------------------
    # URGENCY SCORE
    # ------------------------------------------------

    urgency_map = {

        "Low": 25,

        "Medium": 50,

        "High": 75,

        "Critical": 100
    }


    df["urgency_score"] = (
        df["urgency"]
        .map(urgency_map)
        .fillna(25)
    )


    # ------------------------------------------------
    # BUILD DISTRICT / CATEGORY PRIORITIES
    # ------------------------------------------------

    results = []


    grouped = df.groupby(
        [
            "state",
            "district",
            "category"
        ],
        dropna=False
    )


    for (
        state,
        district,
        category
    ), group in grouped:


        # ============================================
        # CITIZEN DEMAND
        # ============================================

        request_count = len(group)


        # We use log scaling so that a district with
        # thousands of complaints doesn't completely
        # dominate the score.

        demand_score = min(
            100,
            20
            + (
                request_count
                / max(
                    1,
                    len(df)
                )
            )
            * 1000
        )


        # ============================================
        # SEVERITY
        # ============================================

        avg_severity = (
            group[
                "severity_score"
            ].mean()
        )


        # ============================================
        # URGENCY
        # ============================================

        avg_urgency = (
            group[
                "urgency_score"
            ].mean()
        )


        # ============================================
        # POPULATION
        # ============================================

        population_affected = (
            group[
                "affected_population"
            ]
            .fillna(0)
            .sum()
        )


        # Normalize population impact.

        population_score = min(
            100,
            population_affected / 5000
        )


        # ============================================
        # NATIONAL DATA
        # ============================================

        national_data = (
            get_district_data(
                state,
                district
            )
        )


        if national_data:

            infrastructure_gap = float(
                national_data.get(
                    "infrastructure_gap",
                    0
                )
            )


            development_gap = float(
                national_data.get(
                    "development_gap",
                    0
                )
            )


            population = float(
                national_data.get(
                    "population",
                    0
                )
            )


            existing_investment = float(
                national_data.get(
                    "existing_investment",
                    0
                )
            )


            # ========================================
            # NATIONAL INFRASTRUCTURE GAP
            # ========================================

            infrastructure_score = min(
                100,
                infrastructure_gap
            )


            # ========================================
            # DEVELOPMENT GAP
            # ========================================

            development_score = min(
                100,
                development_gap
            )


        else:

            infrastructure_gap = 0

            development_gap = 0

            population = 0

            existing_investment = 0

            infrastructure_score = 0

            development_score = 0


        # ============================================
        # FINAL PRIORITY SCORE
        # ============================================

        priority_score = (

            demand_score * 0.30

            +

            infrastructure_score * 0.25

            +

            population_score * 0.15

            +

            avg_severity * 0.10

            +

            avg_urgency * 0.10

            +

            development_score * 0.10
        )


        priority_score = min(
            100,
            max(
                0,
                priority_score
            )
        )


        # ============================================
        # PRIORITY LEVEL
        # ============================================

        if priority_score >= 80:

            priority_level = "Critical"

        elif priority_score >= 65:

            priority_level = "High"

        elif priority_score >= 45:

            priority_level = "Medium"

        else:

            priority_level = "Low"


        # ============================================
        # RESULT
        # ============================================

        results.append({

            "state":
                state,

            "district":
                district,

            "category":
                category,

            "requests":
                request_count,

            "population":
                population,

            "population_affected":
                population_affected,

            "avg_severity":
                avg_severity,

            "avg_urgency":
                avg_urgency,

            "infrastructure_gap":
                infrastructure_gap,

            "development_gap":
                development_gap,

            "existing_investment":
                existing_investment,

            "demand_score":
                demand_score,

            "infrastructure_score":
                infrastructure_score,

            "population_score":
                population_score,

            "development_score":
                development_score,

            "priority_score":
                priority_score,

            "priority":
                priority_level
        })


    return pd.DataFrame(results)