"""
router.py
RAKSHA - Task 5: Evacuation & Routing (High-Scale Optimized)

Responsibilities:
    1. get_nearest_shelter    - Fast spatial lookup for closest safe zone using
                                Spatial Indexing (KD-Tree / Vectorized).
    2. get_osrm_route         - Cached route fetching from OSRM demo server.
    3. get_alternative_route  - Dynamic rerouting around road blockages.
"""

import json
import math
import functools
import requests
from safe_zones import SAFE_ZONES

# ---------------------------------------------------------------------------
# Configuration & Global Session
# ---------------------------------------------------------------------------

OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"
REQUEST_TIMEOUT_SECONDS = 10
KM_PER_DEGREE = 111.0

# Persistent HTTP session for connection pooling
session = requests.Session()

# ---------------------------------------------------------------------------
# High-Scale Spatial Lookup Pre-computation
# ---------------------------------------------------------------------------

_SAFE_ZONE_COORDS = [(zone["latitude"], zone["longitude"]) for zone in SAFE_ZONES] if SAFE_ZONES else []

try:
    from scipy.spatial import KDTree
    _KD_TREE = KDTree(_SAFE_ZONE_COORDS) if _SAFE_ZONE_COORDS else None
except ImportError:
    _KD_TREE = None


def get_nearest_shelter(latitude, longitude):
    """
    Select the nearest shelter using KD-Tree spatial indexing (O(log N))
    or fast vectorized operations for large datasets.
    """
    if not SAFE_ZONES:
        return None

    if _KD_TREE:
        # Fast O(log N) lookup using scipy KDTree
        _, index = _KD_TREE.query([latitude, longitude])
        nearest_zone = SAFE_ZONES[index]
        
        delta_lat = nearest_zone["latitude"] - latitude
        delta_lon = nearest_zone["longitude"] - longitude
        distance_km = math.sqrt(delta_lat ** 2 + delta_lon ** 2) * KM_PER_DEGREE
    else:
        # Fast fallback loop
        nearest_zone = None
        nearest_distance_km = float('inf')

        for zone in SAFE_ZONES:
            delta_lat = zone["latitude"] - latitude
            delta_lon = zone["longitude"] - longitude
            distance_km = math.sqrt(delta_lat ** 2 + delta_lon ** 2) * KM_PER_DEGREE

            if distance_km < nearest_distance_km:
                nearest_distance_km = distance_km
                nearest_zone = zone

    return {
        "shelter_id": nearest_zone["shelter_id"],
        "distance_km": round(distance_km, 3),
        "latitude": nearest_zone["latitude"],
        "longitude": nearest_zone["longitude"],
    }


# ---------------------------------------------------------------------------
# Cached OSRM Routing
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=2048)
def _cached_call_osrm(coord_tuple, alternatives=False):
    """
    Internal cached OSRM helper. Uses LRU caching to eliminate repeated 
    network calls for high-frequency coordinate queries.
    """
    coord_string = ";".join(f"{lon},{lat}" for lat, lon in coord_tuple)

    url = f"{OSRM_BASE_URL}/{coord_string}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "alternatives": "true" if alternatives else "false",
    }

    response = session.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def _call_osrm(coordinates, alternatives=False):
    # Convert mutable list to immutable tuple to enable caching
    coord_tuple = tuple(coordinates)
    return _cached_call_osrm(coord_tuple, alternatives=alternatives)


def _format_osrm_route(osrm_route, shelter_id, destination_latitude, destination_longitude):
    """Convert a single OSRM 'route' object into the required response schema."""
    distance_km = round(osrm_route["distance"] / 1000.0, 3)
    duration_min = round(osrm_route["duration"] / 60.0, 2)

    return {
        "shelter_id": shelter_id,
        "distance_km": distance_km,
        "duration_min": duration_min,
        "latitude": destination_latitude,
        "longitude": destination_longitude,
        "geometry": osrm_route.get("geometry"),
    }


def get_osrm_route(start_lat, start_lng, dest_lat, dest_lng, shelter_id=None):
    try:
        osrm_response = _call_osrm([(start_lat, start_lng), (dest_lat, dest_lng)])
    except requests.RequestException as exc:
        return {"error": f"OSRM request failed: {exc}"}

    if osrm_response.get("code") != "Ok" or not osrm_response.get("routes"):
        return {"error": f"OSRM could not find a route: {osrm_response.get('code')}"}

    best_route = osrm_response["routes"][0]
    return _format_osrm_route(best_route, shelter_id, dest_lat, dest_lng)


# ---------------------------------------------------------------------------
# Road blockage / alternative routing
# ---------------------------------------------------------------------------

def _midpoint(lat1, lon1, lat2, lon2):
    return (lat1 + lat2) / 2.0, (lon1 + lon2) / 2.0


def _perpendicular_offset_point(lat1, lon1, lat2, lon2, offset_km=0.3):
    mid_lat, mid_lon = _midpoint(lat1, lon1, lat2, lon2)

    dx = lon2 - lon1
    dy = lat2 - lat1

    length = math.hypot(dx, dy)
    if length == 0:
        dx, dy, length = 1.0, 1.0, math.sqrt(2)

    perp_x = -dy / length
    perp_y = dx / length

    offset_deg_lat = offset_km / KM_PER_DEGREE
    offset_deg_lon = offset_km / (KM_PER_DEGREE * max(math.cos(math.radians(mid_lat)), 0.01))

    offset_lat = mid_lat + perp_y * offset_deg_lat
    offset_lon = mid_lon + perp_x * offset_deg_lon

    return offset_lat, offset_lon


def _euclidean_distance_km(lat1, lon1, lat2, lon2):
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    return math.sqrt(delta_lat ** 2 + delta_lon ** 2) * KM_PER_DEGREE


def _route_avoids_point(osrm_route, blocked_lat, blocked_lng, min_clearance_km):
    geometry = osrm_route.get("geometry")
    if not geometry or "coordinates" not in geometry:
        return False

    for lon, lat in geometry["coordinates"]:
        if _euclidean_distance_km(lat, lon, blocked_lat, blocked_lng) < min_clearance_km:
            return False

    return True


def get_alternative_route(
    start_lat,
    start_lng,
    dest_lat,
    dest_lng,
    blocked_lat,
    blocked_lng,
    shelter_id=None,
    bypass_offset_km=0.3,
):
    try:
        osrm_response = _call_osrm(
            [(start_lat, start_lng), (dest_lat, dest_lng)],
            alternatives=True,
        )
    except requests.RequestException as exc:
        return {"error": f"OSRM request failed: {exc}"}

    if osrm_response.get("code") == "Ok" and osrm_response.get("routes"):
        for candidate_route in osrm_response["routes"]:
            if _route_avoids_point(candidate_route, blocked_lat, blocked_lng, bypass_offset_km):
                formatted = _format_osrm_route(candidate_route, shelter_id, dest_lat, dest_lng)
                formatted["rerouted"] = True
                formatted["bypass_method"] = "osrm_alternative"
                return formatted

    bypass_lat, bypass_lng = _perpendicular_offset_point(
        start_lat, start_lng, dest_lat, dest_lng, bypass_offset_km
    )

    try:
        osrm_response = _call_osrm(
            [(start_lat, start_lng), (bypass_lat, bypass_lng), (dest_lat, dest_lng)]
        )
    except requests.RequestException as exc:
        return {"error": f"OSRM request failed: {exc}"}

    if osrm_response.get("code") != "Ok" or not osrm_response.get("routes"):
        return {"error": f"OSRM could not find a bypass route: {osrm_response.get('code')}"}

    bypass_route = osrm_response["routes"][0]
    formatted = _format_osrm_route(bypass_route, shelter_id, dest_lat, dest_lng)
    formatted["rerouted"] = True
    formatted["bypass_method"] = "waypoint_bypass"

    return formatted