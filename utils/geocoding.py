from functools import lru_cache

import requests


NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"

HEADERS = {
    "User-Agent": "JanDrishti-AI/1.0 (Citizen Infrastructure Intelligence Platform)",
    "Accept": "application/json",
    "Accept-Language": "en-IN,en;q=0.9",
}


def _location_data(result, latitude, longitude, fallback_name="Unknown"):
    address = result.get("address", {})

    return {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "village": (
            address.get("village")
            or address.get("hamlet")
            or address.get("suburb")
            or address.get("neighbourhood")
            or address.get("town")
            or address.get("city")
            or fallback_name
        ),
        "district": (
            address.get("state_district")
            or address.get("district")
            or address.get("county")
            or "Unknown"
        ),
        "state": address.get("state", "Unknown"),
        "country": address.get("country", "India"),
        "display_name": result.get(
            "display_name",
            f"{float(latitude):.6f}, {float(longitude):.6f}",
        ),
    }


@lru_cache(maxsize=256)
def geocode_location(location_name: str):
    """Convert a manually entered or AI-extracted place name to coordinates."""
    if not location_name or not str(location_name).strip():
        return None

    clean_location = str(location_name).strip()

    if "india" not in clean_location.lower():
        clean_location = f"{clean_location}, India"

    try:
        response = requests.get(
            NOMINATIM_SEARCH_URL,
            params={
                "q": clean_location,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 1,
                "countrycodes": "in",
                "accept-language": "en",
            },
            headers=HEADERS,
            timeout=(5, 20),
        )
        response.raise_for_status()

        results = response.json()
        if not results:
            return None

        result = results[0]
        return _location_data(
            result=result,
            latitude=result["lat"],
            longitude=result["lon"],
            fallback_name=location_name,
        )

    except (requests.RequestException, ValueError, KeyError, TypeError):
        return None


@lru_cache(maxsize=256)
def reverse_geocode_coordinates(latitude: float, longitude: float):
    """
    Convert browser GPS coordinates into locality, district, state, and country.
    Returns None only if the external lookup is unavailable.
    """
    try:
        response = requests.get(
            NOMINATIM_REVERSE_URL,
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "addressdetails": 1,
                "accept-language": "en",
            },
            headers=HEADERS,
            timeout=(5, 20),
        )
        response.raise_for_status()

        result = response.json()
        return _location_data(
            result=result,
            latitude=latitude,
            longitude=longitude,
            fallback_name="Precise GPS location",
        )

    except (requests.RequestException, ValueError, KeyError, TypeError):
        return None
