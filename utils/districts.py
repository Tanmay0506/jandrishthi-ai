import pandas as pd
from pathlib import Path


DATA_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "district_master.csv"
)


def load_districts():

    if not DATA_PATH.exists():

        raise FileNotFoundError(
            f"District master not found: {DATA_PATH}"
        )

    return pd.read_csv(DATA_PATH)


def district_exists(state, district):

    df = load_districts()

    result = df[
        (df["state"] == state)
        &
        (df["district"] == district)
    ]

    return not result.empty