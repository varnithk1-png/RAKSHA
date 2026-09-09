"""
router.py
RAKSHA - Task 5: Evacuation & Routing

Responsibilities:
    1. get_nearest_shelter    - pick the closest safe zone using straight-line
                                 (Euclidean) distance on lat/lon.
    2. get_osrm_route         - fetch route distance/duration/geometry from
                                 the public OSRM demo server.
    3. get_alternative_route  - simulate a road blockage and recalculate a
                                 route that avoids it.

Only standard/lightweight dependencies are used: `requests`, `json`,
`math`. No PostgreSQL/PostGIS or heavy geospatial libraries, per the MVP
scope freeze.

JSON output key names are fixed per the shared API contract:
    shelter_id, distance_km, duration_min, latitude, longitude
"""

import json
import math
import requests

from safe_zones import SAFE_ZONES

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"
REQUEST_TIMEOUT_SECONDS = 10

# Rough km-per-degree used to convert Euclidean (lat/lon) distance into an
# approximate km figure for display purposes. This is NOT geodesically
# precise -- it is a simple, fast estimate suitable for picking "which
# shelter is closest" during the MVP, not for turn-by-turn navigation.
KM_PER_DEGREE = 111.0


# ---------------------------------------------------------------------------
# Safe-zone selection (Euclidean distance)
# ---------------------------------------------------------------------------

def get_nearest_shelter(latitude, longitude):
    """
    Select the nearest shelter from SAFE_ZONES using straight-line
    (Euclidean) distance on raw lat/lon coordinates.

    This is intentionally simple for the MVP: over the small distances
    involved in a single study area, Euclidean distance on lat/lon is a
    reasonable and fast approximation for "which shelter is closest",
    with the real travel distance/time later confirmed by OSRM in
    get_osrm_route().

    Args:
        latitude (float): victim/user latitude.
        longitude (float): victim/user longitude.

    Returns:
        dict: {
            "shelter_id": ...,
            "distance_km": ...,
            "latitude": ...,
            "longitude": ...
        }
        or None if SAFE_ZONES is empty.
    """
    if not SAFE_ZONES:
        return None

    nearest_zone = None
    nearest_distance_km = None

    for zone in SAFE_ZONES:
        delta_lat = zone["latitude"] - latitude
        delta_lon = zone["longitude"] - longitude

        # Plain Euclidean distance in degrees, converted to an approximate
        # km value using KM_PER_DEGREE.
        euclidean_degrees = math.sqrt(delta_lat ** 2 + delta_lon ** 2)
        distance_km = euclidean_degrees * KM_PER_DEGREE

        if nearest_distance_km is None or distance_km < nearest_distance_km:
            nearest_distance_km = distance_km
            nearest_zone = zone

    return {
        "shelter_id": nearest_zone["shelter_id"],
        "distance_km": round(nearest_distance_km, 3),
        "latitude": nearest_zone["latitude"],
        "longitude": nearest_zone["longitude"],
    }


# ---------------------------------------------------------------------------
# OSRM routing
# ---------------------------------------------------------------------------

def _call_osrm(coordinates, alternatives=False):
    """
    Internal helper: call the OSRM demo server with a list of
    (latitude, longitude) tuples defining the route waypoints, in order.

    Returns the parsed JSON response from OSRM, or raises
    requests.RequestException on network/HTTP failure.
    """
    # OSRM expects "lon,lat" pairs separated by ";".
    coord_string = ";".join(f"{lon},{lat}" for lat, lon in coordinates)

    url = f"{OSRM_BASE_URL}/{coord_string}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "alternatives": "true" if alternatives else "false",
    }

    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()

    return response.json()


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
    """
    Fetch a real driving route from OSRM between a start point and a
    destination (typically a safe zone).

    Args:
        start_lat, start_lng (float): victim/user location.
        dest_lat, dest_lng (float): destination (shelter) location.
        shelter_id (str, optional): included in the response for the
            frontend/map to correlate the route with the selected shelter.

    Returns:
        dict: {
            "shelter_id": ...,
            "distance_km": ...,
            "duration_min": ...,
            "latitude": ...,      # destination latitude
            "longitude": ...,     # destination longitude
            "geometry": ...       # GeoJSON LineString, for map display
        }
        or {"error": "..."} on failure.
    """
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
    """Simple arithmetic midpoint of two coordinates."""
    return (lat1 + lat2) / 2.0, (lon1 + lon2) / 2.0


def _perpendicular_offset_point(lat1, lon1, lat2, lon2, offset_km=0.3):
    """
    Given a line segment (lat1, lon1) -> (lat2, lon2), return a point offset
    perpendicular to the segment's midpoint by `offset_km`. Used to build a
    bypass waypoint that steers OSRM's route away from a blocked road
    segment.
    """
    mid_lat, mid_lon = _midpoint(lat1, lon1, lat2, lon2)

    dx = lon2 - lon1
    dy = lat2 - lat1

    length = math.hypot(dx, dy)
    if length == 0:
        dx, dy, length = 1.0, 1.0, math.sqrt(2)

    # Unit perpendicular vector (rotate direction by 90 degrees).
    perp_x = -dy / length
    perp_y = dx / length

    offset_deg_lat = offset_km / KM_PER_DEGREE
    offset_deg_lon = offset_km / (KM_PER_DEGREE * max(math.cos(math.radians(mid_lat)), 0.01))

    offset_lat = mid_lat + perp_y * offset_deg_lat
    offset_lon = mid_lon + perp_x * offset_deg_lon

    return offset_lat, offset_lon


def _euclidean_distance_km(lat1, lon1, lat2, lon2):
    """Same approximate Euclidean-distance-to-km conversion used in
    get_nearest_shelter(), reused here to check clearance from a blocked
    point."""
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    return math.sqrt(delta_lat ** 2 + delta_lon ** 2) * KM_PER_DEGREE


def _route_avoids_point(osrm_route, blocked_lat, blocked_lng, min_clearance_km):
    """
    Check whether every coordinate along an OSRM route's geometry stays at
    least `min_clearance_km` away from the blocked point. A coarse but
    sufficient check for MVP purposes (no PostGIS spatial indexing used).
    """
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
    """
    Simulate a reported road blockage near (blocked_lat, blocked_lng) on the
    path from start to destination, and recalculate a route around it.

    Strategy:
        1. Ask OSRM directly for alternative routes (alternatives=true).
           If any alternative route's geometry stays reasonably far
           (> bypass_offset_km) from the blocked point, use it.
        2. If no suitable OSRM alternative is found, fall back to inserting
           a synthetic bypass waypoint offset perpendicular to the
           start->destination line near the blocked point, and re-request
           a route through that waypoint.

    Args:
        start_lat, start_lng (float): victim/user location.
        dest_lat, dest_lng (float): destination (shelter) location.
        blocked_lat, blocked_lng (float): reported/simulated blockage location.
        shelter_id (str, optional): included in the response.
        bypass_offset_km (float): minimum clearance (km) a route must keep
            from the blocked point, and the offset used when constructing a
            synthetic bypass waypoint.

    Returns:
        dict: same schema as get_osrm_route(), plus:
            "rerouted": True
            "bypass_method": "osrm_alternative" | "waypoint_bypass"
        or {"error": "..."} on failure.
    """
    # --- Attempt 1: use OSRM's native alternative routes ---
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

    # --- Attempt 2: insert a synthetic bypass waypoint ---
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


# ---------------------------------------------------------------------------
# Manual test / demo entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    victim_lat, victim_lng = 17.3616, 78.4747

    nearest = get_nearest_shelter(victim_lat, victim_lng)
    print("Nearest shelter (Euclidean distance):")
    print(json.dumps(nearest, indent=2))

    if nearest:
        route = get_osrm_route(
            victim_lat, victim_lng,
            nearest["latitude"], nearest["longitude"],
            shelter_id=nearest["shelter_id"],
        )
        print("\nOSRM route:")
        print(json.dumps(route, indent=2))

        # Simulate a blockage roughly midway along the route.
        mid_lat, mid_lng = _midpoint(
            victim_lat, victim_lng, nearest["latitude"], nearest["longitude"]
        )

        alt_route = get_alternative_route(
            victim_lat, victim_lng,
            nearest["latitude"], nearest["longitude"],
            mid_lat, mid_lng,
            shelter_id=nearest["shelter_id"],
        )
        print("\nAlternative route (after simulated blockage):")
        print(json.dumps(alt_route, indent=2))
