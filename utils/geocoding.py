import requests
import time
from urllib.parse import quote


# --------------------------------------------------
# Nominatim Configuration
# --------------------------------------------------

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {
    "User-Agent": (
        "JanDrishti-AI/1.0 "
        "(Citizen Infrastructure Intelligence Platform)"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-IN,en;q=0.9",
}


# --------------------------------------------------
# Geocode Location
# --------------------------------------------------

def geocode_location(location_name: str):
    """
    Convert a location name into latitude/longitude
    and administrative information using OpenStreetMap
    Nominatim.

    Designed to work reliably on cloud deployments
    such as Render and Streamlit Cloud.
    """

    if not location_name:
        return None

    location_name = str(location_name).strip()

    if not location_name:
        return None

    # --------------------------------------------------
    # Improve Indian location searches
    # --------------------------------------------------

    search_query = location_name

    # If user hasn't specified India, bias search toward India.
    if "india" not in location_name.lower():
        search_query = f"{location_name}, India"

    params = {
        "q": search_query,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 1,
        "countrycodes": "in",
        "accept-language": "en",
    }

    # --------------------------------------------------
    # Retry mechanism
    # --------------------------------------------------

    max_retries = 3

    for attempt in range(max_retries):

        try:

            response = requests.get(
                NOMINATIM_URL,
                params=params,
                headers=HEADERS,
                timeout=(5, 20),
            )

            # --------------------------------------------------
            # Rate limited
            # --------------------------------------------------

            if response.status_code == 429:

                # Wait before retrying
                time.sleep(2 + attempt * 2)

                continue

            # --------------------------------------------------
            # Server temporarily unavailable
            # --------------------------------------------------

            if response.status_code in (500, 502, 503, 504):

                time.sleep(2 + attempt * 2)

                continue

            response.raise_for_status()

            # --------------------------------------------------
            # Parse JSON
            # --------------------------------------------------

            results = response.json()

            if not results:
                return None

            result = results[0]

            # --------------------------------------------------
            # Coordinates
            # --------------------------------------------------

            latitude = result.get("lat")
            longitude = result.get("lon")

            if latitude is None or longitude is None:
                return None

            latitude = float(latitude)
            longitude = float(longitude)

            # --------------------------------------------------
            # Address information
            # --------------------------------------------------

            address = result.get("address", {})

            village = (
                address.get("village")
                or address.get("hamlet")
                or address.get("town")
                or address.get("city")
                or address.get("municipality")
                or address.get("suburb")
                or address.get("neighbourhood")
                or "Unknown"
            )

            district = (
                address.get("state_district")
                or address.get("district")
                or address.get("county")
                or "Unknown"
            )

            state = (
                address.get("state")
                or address.get("state_district")
                or "Unknown"
            )

            country = (
                address.get("country")
                or "India"
            )

            postcode = (
                address.get("postcode")
                or "Unknown"
            )

            # --------------------------------------------------
            # Return structured result
            # --------------------------------------------------

            return {
                "latitude": latitude,
                "longitude": longitude,

                "village": village,

                "district": district,

                "state": state,

                "country": country,

                "postcode": postcode,

                "display_name": result.get(
                    "display_name",
                    location_name
                ),
            }

        # --------------------------------------------------
        # Network errors
        # --------------------------------------------------

        except requests.exceptions.Timeout:

            if attempt < max_retries - 1:
                time.sleep(2)
                continue

            return None

        except requests.exceptions.ConnectionError:

            if attempt < max_retries - 1:
                time.sleep(2)
                continue

            return None

        except requests.exceptions.RequestException:

            return None

        # --------------------------------------------------
        # Invalid response
        # --------------------------------------------------

        except (ValueError, KeyError, TypeError):

            return None

    return None
