[README (3).md](https://github.com/user-attachments/files/32018655/README.3.md)[Uploading # Task 5 — Evacuation & Routing

Owns: safe-zone selection, OSRM routing, and blockage rerouting for RAKSHA.

## Files

```
routing/
├── data/
│   └── safe_zones.geojson   # shelter locations (SWAP THIS with Task 3's real file)
├── safe_zones_loader.py     # reads safe_zones.geojson into Python dicts
├── router.py                # all routing/recommendation logic
├── requirements.txt
└── README.md
```

## Why this isn't hardcoded to a few places

The first version of this module had a Python list of ~5 shelters baked
directly into the code, and used a flat-plane distance approximation
calibrated to one city. That meant:
- Adding/updating shelters meant editing code.
- Distance accuracy degraded the further you got from wherever the
  approximation was tuned.

This version fixes both:
- **Shelters live in `data/safe_zones.geojson`**, a standard GeoJSON file.
  Task 3 (GIS) can replace this file with the real, verified shelter
  dataset at any time — nobody touches Python code. `router.py` doesn't
  know or care how many shelters there are or where they are.
- **Distance uses the haversine formula** (`_haversine_km`), which is
  accurate anywhere on Earth, not just near one calibration point.
- Every function takes raw `latitude`/`longitude` arguments, so it works
  for any point the frontend map or GPS sends — there's no allow-list of
  "supported" coordinates.

## Swapping in the real GIS data

Replace `data/safe_zones.geojson` with Task 3's file, keeping this shape:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [LONGITUDE, LATITUDE] },
      "properties": { "shelter_id": "SZ001", "name": "..." }
    }
  ]
}
```
(Note GeoJSON order is `[lon, lat]`, not `[lat, lon]`.) Only `shelter_id`
(or `id`) is required in `properties`; everything else is optional and
passed through untouched. If your backend deploys the file to a different
path, set the `RAKSHA_SAFE_ZONES_PATH` environment variable instead of
editing code.

## Public functions (for Task 1 / backend to import)

```python
from router import (
    get_ranked_shelters,
    get_nearest_shelter,
    get_osrm_route,
    recommend_safe_zone,
    get_alternative_route,
)
```

| Function | Purpose |
|---|---|
| `get_ranked_shelters(lat, lon, top_n=None)` | All shelters, sorted by straight-line distance. |
| `get_nearest_shelter(lat, lon)` | Fast single closest shelter (straight-line only, no network call — useful as an offline fallback). |
| `get_osrm_route(start_lat, start_lng, dest_lat, dest_lng)` | Real driving route between any two points via OSRM. |
| `recommend_safe_zone(lat, lon, k_candidates=3)` | **The main entry point.** See below. |
| `get_alternative_route(start_lat, start_lng, dest_lat, dest_lng, blocked_lat, blocked_lng)` | Reroute around a reported/simulated blockage. |

All functions raise `ValueError` on out-of-range coordinates and return
`{"error": "..."}` (not an exception) on OSRM/network failures, so the
backend can handle both cases explicitly.

## How safe-zone recommendation works (and why)

`recommend_safe_zone()` answers "why this shelter?" for *any* location:

1. Take the `k_candidates` nearest shelters by straight-line distance
   (cheap, no network calls — fine even with hundreds of shelters loaded).
2. Ask OSRM for the actual road distance/time to each of those candidates.
   The straight-line-nearest shelter isn't always the fastest to actually
   reach (one-way streets, a river, a highway with no nearby crossing).
3. Recommend whichever *reachable* candidate has the shortest real travel
   time, and return a `reasoning` string explaining the choice plus a
   `candidates_considered` list for transparency/debugging on the
   responder dashboard.

This keeps OSRM calls bounded (default: 3 per request) instead of querying
every shelter in the city, while still making a road-aware — not just
as-the-crow-flies — recommendation.

## How rerouting (blockage handling) works

`get_alternative_route()` takes a reported/simulated blockage point and:

1. First asks OSRM for its own alternative routes and checks if any of
   them already stay clear of the blockage (`_route_avoids_point`,
   using the same haversine distance as everything else).
2. If none do, it computes a synthetic bypass waypoint offset
   perpendicular to the direct start→destination line near the blockage,
   and asks OSRM to route through that waypoint instead.

The response includes `"rerouted": true` and `"bypass_method"` so the
frontend/map can visually flag that this is a rerouted path.

## Scope (per team scope-freeze)

No custom routing engine, no PostGIS, no shelter-reallocation/capacity
optimization. Shelter *selection* (which one to recommend) is intentionally
simple (nearest-by-road among top-K), matching the MVP scope.

## Local setup

```bash
pip install -r requirements.txt
python router.py   # runs a demo across 3 different points in the city
```

## Integration contract (for Task 1 / backend)

Wrap these functions in your FastAPI endpoints, e.g.:

```python
from routing.router import recommend_safe_zone, get_alternative_route

@app.get("/api/recommend-shelter")
def recommend_shelter(lat: float, lon: float):
    return recommend_safe_zone(lat, lon)

@app.get("/api/reroute")
def reroute(lat: float, lon: float, shelter_lat: float, shelter_lon: float,
            blocked_lat: float, blocked_lon: float):
    return get_alternative_route(lat, lon, shelter_lat, shelter_lon, blocked_lat, blocked_lon)
```

Response JSON keys are fixed: `shelter_id`, `distance_km`, `duration_min`,
`latitude`, `longitude` (plus `geometry` for map rendering, and
`reasoning`/`rerouted`/`bypass_method` where relevant).
README (3).md…]()
