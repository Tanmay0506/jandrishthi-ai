import pandas as pd
from pathlib import Path


DATA_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "national_infrastructure.csv"
)


def load_national_data():

    if not DATA_PATH.exists():

        raise FileNotFoundError(
            f"National infrastructure dataset "
            f"not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    return df


def get_district_data(
    state,
    district
):

    df = load_national_data()

    result = df[
        (df["state"] == state)
        &
        (df["district"] == district)
    ]

    if result.empty:

        return None

    return result.iloc[0].to_dict()