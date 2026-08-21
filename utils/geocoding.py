import requests


def geocode_location(location_name: str):
    """
    Convert a location name into latitude/longitude
    and basic administrative information using
    OpenStreetMap Nominatim.
    """

    if not location_name or not location_name.strip():
        return None

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": location_name.strip(),
        "format": "json",
        "addressdetails": 1,
        "limit": 1,
    }

    headers = {
        "User-Agent": "JanDrishti-AI/1.0"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        results = response.json()

        if not results:
            return None

        result = results[0]
        address = result.get("address", {})

        return {
            "latitude": float(result["lat"]),
            "longitude": float(result["lon"]),

            "village": (
                address.get("village")
                or address.get("town")
                or address.get("city")
                or address.get("municipality")
                or "Unknown"
            ),

            "district": (
                address.get("county")
                or address.get("district")
                or "Unknown"
            ),

            "state": address.get("state", "Unknown"),
            "country": address.get("country", "India"),

            "display_name": result.get(
                "display_name",
                location_name
            ),
        }

    except requests.RequestException:
        return None

    except (ValueError, KeyError, TypeError):
        return None 