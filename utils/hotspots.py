import pandas as pd
import numpy as np

from sklearn.cluster import DBSCAN


def detect_hotspots(df):

    if df.empty:
        return pd.DataFrame()

    # Remove records without coordinates
    geo_df = df.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    if geo_df.empty:
        return pd.DataFrame()

    coordinates = geo_df[
        ["latitude", "longitude"]
    ].to_numpy()

    # DBSCAN using geographic distance
    # Approximately 5 km neighborhood
    kms_per_radian = 6371.0088

    epsilon_km = 5

    epsilon = (
        epsilon_km / kms_per_radian
    )

    coords_radians = np.radians(
        coordinates
    )

    clustering = DBSCAN(
        eps=epsilon,
        min_samples=10,
        algorithm="ball_tree",
        metric="haversine"
    )

    geo_df["cluster"] = clustering.fit_predict(
        coords_radians
    )

    # -1 = noise / isolated requests
    hotspots = geo_df[
        geo_df["cluster"] != -1
    ]

    if hotspots.empty:
        return pd.DataFrame()

    # Aggregate clusters
    result = (
        hotspots
        .groupby("cluster")
        .agg(
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
            requests=("id", "count"),
            population_affected=(
                "affected_population",
                "sum"
            ),
            state=("state", "first"),
            district=("district", "first")
        )
        .reset_index()
    )

    # Calculate hotspot intensity
    result["intensity"] = (
        result["requests"]
        / result["requests"].max()
        * 100
    )

    result["intensity"] = (
        result["intensity"]
        .round(2)
    )

    return result.sort_values(
        "intensity",
        ascending=False
    )