import pandas as pd
from pathlib import Path


DATA_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "external"
    / "development_indicators.csv"
)


def load_development_data():

    return pd.read_csv(DATA_PATH)


def get_district_indicator(
    state,
    district
):

    df = load_development_data()

    result = df[
        (df["state"] == state)
        &
        (df["district"] == district)
    ]

    if result.empty:
        return None

    return result.iloc[0].to_dict()