import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org"


def _extract_location(result, latitude, longitude):
    """
    Convert Nominatim response into a clean JanDrishti location object.
    """

    if not result:
        return None

    address = result.get("address", {})

    village = (
        address.get("village")
        or address.get("town")
        or address.get("city")
        or address.get("municipality")
        or address.get("suburb")
        or address.get("neighbourhood")
        or "Unknown"
    )

    sub_district = (
        address.get("subdistrict")
        or address.get("tehsil")
        or address.get("taluk")
        or address.get("township")
        or address.get("municipality")
        or "Unknown"
    )

    district = (
        address.get("county")
        or address.get("district")
        or "Unknown"
    )

    state = address.get(
        "state",
        "Unknown"
    )

    country = address.get(
        "country",
        "India"
    )

    return {
        "latitude": float(latitude),
        "longitude": float(longitude),

        "village": village,

        "sub_district": sub_district,

        "district": district,

        "state": state,

        "country": country,

        "display_name": result.get(
            "display_name",
            "GPS Location"
        ),
    }


# ============================================================
# GPS → LOCATION
# ============================================================

def reverse_geocode(latitude, longitude):
    """
    Convert GPS latitude/longitude into:
    village, sub-district, district and state.
    """

    if latitude is None or longitude is None:
        return None

    try:

        latitude = float(latitude)
        longitude = float(longitude)

        headers = {
            "User-Agent": (
                "JanDrishti-AI/1.0 "
                "(citizen infrastructure mapping)"
            )
        }

        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "addressdetails": 1,
            "zoom": 18
        }

        response = requests.get(
            f"{NOMINATIM_URL}/reverse",
            params=params,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        result = response.json()

        return _extract_location(
            result,
            latitude,
            longitude
        )

    except Exception as e:

        print(
            "Reverse geocoding error:",
            str(e)
        )

        return None


# ============================================================
# TEXT → LOCATION
# ============================================================

def geocode_location(location_name):
    """
    Convert manually entered location into coordinates.
    """

    if not location_name:
        return None

    location_name = location_name.strip()

    if not location_name:
        return None

    try:

        headers = {
            "User-Agent": (
                "JanDrishti-AI/1.0 "
                "(citizen infrastructure mapping)"
            )
        }

        params = {
            "q": location_name,
            "format": "json",
            "addressdetails": 1,
            "limit": 1,
            "countrycodes": "in"
        }

        response = requests.get(
            f"{NOMINATIM_URL}/search",
            params=params,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        results = response.json()

        if not results:
            return None

        result = results[0]

        latitude = float(
            result["lat"]
        )

        longitude = float(
            result["lon"]
        )

        return _extract_location(
            result,
            latitude,
            longitude
        )

    except Exception as e:

        print(
            "Geocoding error:",
            str(e)
        )

        return None
