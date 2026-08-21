import sqlite3
import pandas as pd
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).parent.parent
    / "database"
    / "jandrishthi.db"
)


def load_requests():

    connection = sqlite3.connect(DATABASE_PATH)

    df = pd.read_sql_query(
        """
        SELECT *
        FROM citizen_requests
        ORDER BY created_at DESC
        """,
        connection
    )

    connection.close()

    return df


def category_counts():

    df = load_requests()

    if df.empty:
        return pd.DataFrame()

    return (
        df["category"]
        .value_counts()
        .reset_index()
        .rename(
            columns={
                "category": "Category",
                "count": "Requests"
            }
        )
    )


def state_counts():

    df = load_requests()

    if df.empty:
        return pd.DataFrame()

    return (
        df["state"]
        .value_counts()
        .reset_index()
        .rename(
            columns={
                "state": "State",
                "count": "Requests"
            }
        )
    )


def district_counts():

    df = load_requests()

    if df.empty:
        return pd.DataFrame()

    return (
        df["district"]
        .value_counts()
        .reset_index()
        .rename(
            columns={
                "district": "District",
                "count": "Requests"
            }
        )
    )


def severity_counts():

    df = load_requests()

    if df.empty:
        return pd.DataFrame()

    severity_order = [
        "Critical",
        "High",
        "Medium",
        "Low"
    ]

    counts = (
        df["severity"]
        .value_counts()
        .reindex(severity_order)
        .fillna(0)
        .reset_index()
    )

    counts.columns = [
        "Severity",
        "Requests"
    ]

    return counts