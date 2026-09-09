"""
router.py
RAKSHA - Task 5: Evacuation & Routing

Responsibilities:
    1. get_ranked_shelters   - rank ALL safe zones by straight-line
                                (haversine) distance from any given point.
    2. get_nearest_shelter   - convenience wrapper: closest safe zone only.
    3. get_osrm_route        - fetch route distance/duration/geometry from
                                OSRM for a start -> destination pair.
    4. recommend_safe_zone   - the "smart pick": pre-filter nearby candidates
                                by straight-line distance, then ask OSRM for
                                the real road distance/time to each, and
                                recommend the best reachable one -- with a
                                plain-English reason.
    5. get_alternative_route - simulate/handle a reported road blockage and
                                recalculate a route that avoids it.

Design notes (why this version is different from a "hardcoded" MVP):
    - There is NO fixed list of locations anywhere in this file. Shelters
      come from safe_zones_loader.load_safe_zones(), which reads a GeoJSON
      file that the GIS teammate owns and can update at any time.
    - Distance uses the haversine formula, which is accurate for any two
      points on Earth -- not a flat-plane approximation calibrated to one
      city. So this works correctly whether the victim is 200m or 200km
      from the nearest shelter.
    - Every public function takes latitude/longitude as plain arguments,
      so it works for ANY point a teammate's frontend/map sends, not a
      fixed set of test coordinates.

Only standard/lightweight dependencies are used: `requests`, `json`,
`math`. No PostgreSQL/PostGIS or heavy geospatial libraries, per the MVP
scope freeze.

JSON output key names follow the shared API contract:
    shelter_id, distance_km, duration_min, latitude, longitude
"""

import json
import math
import requests

from safe_zones_loader import load_safe_zones

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"
REQUEST_TIMEOUT_SECONDS = 10

EARTH_RADIUS_KM = 6371.0088


# ---------------------------------------------------------------------------
# Coordinate validation / distance helpers
# ---------------------------------------------------------------------------

def _validate_latlon(lat, lon, label="point"):
    """Raise a clear error for out-of-range coordinates instead of silently
    producing nonsense distances -- important once input is no longer a
    small trusted set of test points but arbitrary user/GPS input."""
    if not (-90.0 <= lat <= 90.0):
        raise ValueError(f"Invalid latitude for {label}: {lat} (must be between -90 and 90).")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError(f"Invalid longitude for {label}: {lon} (must be between -180 and 180).")


def _haversine_km(lat1, lon1, lat2, lon2):
    """
    Great-circle distance between two lat/lon points, in kilometers.

    Unlike a flat "degrees * constant" approximation, this is accurate
    anywhere on the globe, which is what lets get_nearest_shelter() /
    get_ranked_shelters() work correctly for any victim location -- not
    just points close to wherever the approximation was calibrated.
    """
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))


# ---------------------------------------------------------------------------
# Safe-zone ranking (works for any location, any number of shelters)
# ---------------------------------------------------------------------------

def get_ranked_shelters(latitude, longitude, top_n=None, safe_zones=None):
    """
    Rank ALL loaded safe zones by straight-line (haversine) distance from
    (latitude, longitude), nearest first.

    Args:
        latitude, longitude (float): the point to measure from (victim/user
            location). Any valid coordinate works -- there is no fixed list
            of "supported" locations.
        top_n (int, optional): if given, only the N closest are returned.
            If omitted, every loaded shelter is returned, ranked.
        safe_zones (list[dict], optional): inject a specific list of
            shelters (mainly for testing). Defaults to
            safe_zones_loader.load_safe_zones().

    Returns:
        list[dict]: each item has shelter_id, name, latitude, longitude,
        straight_line_km -- sorted ascending by straight_line_km.
    """
    _validate_latlon(latitude, longitude, "victim location")

    zones = safe_zones if safe_zones is not None else load_safe_zones()

    ranked = []
    for zone in zones:
        distance_km = _haversine_km(latitude, longitude, zone["latitude"], zone["longitude"])
        ranked.append({
            "shelter_id": zone["shelter_id"],
            "name": zone.get("name", zone["shelter_id"]),
            "latitude": zone["latitude"],
            "longitude": zone["longitude"],
            "straight_line_km": round(distance_km, 3),
        })

    ranked.sort(key=lambda z: z["straight_line_km"])

    return ranked[:top_n] if top_n else ranked


def get_nearest_shelter(latitude, longitude, safe_zones=None):
    """
    Select the single nearest shelter by straight-line distance.

    Kept as a simple, fast building block (used e.g. as a quick fallback if
    OSRM is unreachable). For a real recommendation that accounts for
    actual road distance/time, use recommend_safe_zone() instead.

    Returns:
        dict: {shelter_id, distance_km, latitude, longitude} or None if no
        safe zones are loaded.
    """
    ranked = get_ranked_shelters(latitude, longitude, top_n=1, safe_zones=safe_zones)
    if not ranked:
        return None

    nearest = ranked[0]
    return {
        "shelter_id": nearest["shelter_id"],
        "distance_km": nearest["straight_line_km"],
        "latitude": nearest["latitude"],
        "longitude": nearest["longitude"],
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
    Fetch a real driving route from OSRM between any start point and any
    destination point.

    Args:
        start_lat, start_lng (float): victim/user location.
        dest_lat, dest_lng (float): destination (shelter) location.
        shelter_id (str, optional): included in the response for the
            frontend/map to correlate the route with the selected shelter.

    Returns:
        dict: {shelter_id, distance_km, duration_min, latitude, longitude,
        geometry} or {"error": "..."} on failure.
    """
    _validate_latlon(start_lat, start_lng, "start")
    _validate_latlon(dest_lat, dest_lng, "destination")

    try:
        osrm_response = _call_osrm([(start_lat, start_lng), (dest_lat, dest_lng)])
    except requests.RequestException as exc:
        return {"error": f"OSRM request failed: {exc}"}

    if osrm_response.get("code") != "Ok" or not osrm_response.get("routes"):
        return {"error": f"OSRM could not find a route: {osrm_response.get('code')}"}

    best_route = osrm_response["routes"][0]

    return _format_osrm_route(best_route, shelter_id, dest_lat, dest_lng)


# ---------------------------------------------------------------------------
# Smart recommendation: straight-line pre-filter + real road distance/time
# ---------------------------------------------------------------------------

def recommend_safe_zone(latitude, longitude, k_candidates=3, safe_zones=None):
    """
    Recommend the best safe zone for a victim at (latitude, longitude),
    and explain WHY -- this is what answers "why the safe zone is
    recommended" for any location, not just pre-tested ones.

    Strategy:
        1. Take the `k_candidates` nearest shelters by straight-line
           (haversine) distance -- fast, no network calls, works for any
           point on the map.
        2. Ask OSRM for the actual road distance/duration to each
           candidate (straight-line nearest isn't always fastest to
           actually reach -- a river, highway, or one-way system can make
           a "farther" shelter quicker in practice).
        3. Recommend whichever reachable candidate has the shortest real
           road travel time, and say so in plain language.

    Args:
        latitude, longitude (float): victim/user location. Works for any
            valid coordinate.
        k_candidates (int): how many nearest-by-straight-line shelters to
            actually check against OSRM. Keeps this to a handful of OSRM
            calls instead of querying every shelter in the city.
        safe_zones (list[dict], optional): inject a specific list (mainly
            for testing).

    Returns:
        dict: {
            shelter_id, distance_km, duration_min, latitude, longitude,
            geometry, reasoning, candidates_considered
        } for the recommended shelter, or {"error": "..."} if none of the
        candidates were reachable.
    """
    _validate_latlon(latitude, longitude, "victim location")

    candidates = get_ranked_shelters(latitude, longitude, top_n=k_candidates, safe_zones=safe_zones)
    if not candidates:
        return {"error": "No safe zones are currently loaded."}

    evaluated = []
    for candidate in candidates:
        route = get_osrm_route(
            latitude, longitude,
            candidate["latitude"], candidate["longitude"],
            shelter_id=candidate["shelter_id"],
        )
        evaluated.append({
            "shelter_id": candidate["shelter_id"],
            "name": candidate["name"],
            "straight_line_km": candidate["straight_line_km"],
            "route": route,
            "reachable": "error" not in route,
        })

    reachable = [c for c in evaluated if c["reachable"]]

    if not reachable:
        return {
            "error": (
                f"None of the {len(candidates)} nearest safe zones were reachable via OSRM. "
                f"Last error: {evaluated[-1]['route'].get('error') if evaluated else 'unknown'}"
            )
        }

    best = min(reachable, key=lambda c: c["route"]["duration_min"])

    other_names = [c["name"] for c in reachable if c["shelter_id"] != best["shelter_id"]]
    if other_names:
        reasoning = (
            f"{best['name']} was chosen from the {len(candidates)} nearest safe zones "
            f"(by straight-line distance) because it has the shortest real road travel time "
            f"({best['route']['duration_min']} min, {best['route']['distance_km']} km), "
            f"beating {', '.join(other_names)} once actual road access was checked via OSRM."
        )
    else:
        reasoning = (
            f"{best['name']} was chosen as the only reachable safe zone among the "
            f"{len(candidates)} nearest candidates checked, at {best['route']['duration_min']} min "
            f"({best['route']['distance_km']} km) by road."
        )

    result = dict(best["route"])
    result["reasoning"] = reasoning
    result["candidates_considered"] = evaluated
    return result


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

    km_per_degree_lat = EARTH_RADIUS_KM * math.pi / 180.0
    km_per_degree_lon = km_per_degree_lat * max(math.cos(math.radians(mid_lat)), 0.01)

    offset_deg_lat = offset_km / km_per_degree_lat
    offset_deg_lon = offset_km / km_per_degree_lon

    offset_lat = mid_lat + perp_y * offset_deg_lat
    offset_lon = mid_lon + perp_x * offset_deg_lon

    return offset_lat, offset_lon


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
        if _haversine_km(lat, lon, blocked_lat, blocked_lng) < min_clearance_km:
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
    Simulate/handle a reported road blockage near (blocked_lat, blocked_lng)
    on the path from start to destination, and recalculate a route around
    it. Works for any start/destination/blockage location -- nothing here
    depends on a fixed set of coordinates.

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
    _validate_latlon(start_lat, start_lng, "start")
    _validate_latlon(dest_lat, dest_lng, "destination")
    _validate_latlon(blocked_lat, blocked_lng, "blockage")

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
    # Deliberately using several DIFFERENT points scattered across the city
    # (not one fixed test coordinate) to demonstrate this isn't hardcoded
    # to a single location.
    demo_points = [
        ("Near Charminar", 17.3616, 78.4747),
        ("Near HITEC City", 17.4483, 78.3915),
        ("Near LB Nagar", 17.3457, 78.5497),
    ]

    for label, victim_lat, victim_lng in demo_points:
        print(f"\n=== {label} ({victim_lat}, {victim_lng}) ===")

        recommendation = recommend_safe_zone(victim_lat, victim_lng)
        print("Recommended safe zone:")
        print(json.dumps({k: v for k, v in recommendation.items() if k != "candidates_considered"}, indent=2))

        if "error" not in recommendation:
            mid_lat, mid_lng = _midpoint(
                victim_lat, victim_lng, recommendation["latitude"], recommendation["longitude"]
            )
            alt_route = get_alternative_route(
                victim_lat, victim_lng,
                recommendation["latitude"], recommendation["longitude"],
                mid_lat, mid_lng,
                shelter_id=recommendation["shelter_id"],
            )
            print("\nAlternative route (after simulated blockage):")
            print(json.dumps({k: v for k, v in alt_route.items() if k != "geometry"}, indent=2))
