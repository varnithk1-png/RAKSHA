"""
safe_zones_loader.py
RAKSHA - Task 5: Evacuation & Routing

Loads safe-zone (shelter) data from a GeoJSON file instead of a hardcoded
Python list. This is the key fix that lets the routing logic work for the
WHOLE map instead of a handful of baked-in coordinates:

    - The GIS teammate (Task 3) can update/replace `data/safe_zones.geojson`
      at any time -- with real, verified shelters -- and router.py picks up
      the change automatically. No code changes needed.
    - Any number of shelters, anywhere, is supported. There is nothing in
      this file that limits location or count.

Expected GeoJSON shape (standard FeatureCollection of Points):

    {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": { "type": "Point", "coordinates": [lon, lat] },
          "properties": {
            "shelter_id": "SZ001",   // required (or "id")
            "name": "...",           // optional
            "capacity": 2000         // optional, any extra properties are
                                      // passed through untouched
          }
        },
        ...
      ]
    }

Note: GeoJSON coordinate order is [longitude, latitude] -- this is a very
common source of bugs, so it is handled once, here, and nowhere else.
"""

import os
import json

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Default location of the safe-zones file, relative to this module, so it
# works regardless of the current working directory the backend runs from.
_DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "safe_zones.geojson")

# Allow overriding the path via environment variable, e.g. if the GIS
# teammate's file lives elsewhere in the deployed backend (Task 1 can set
# this without touching Task 5's code).
ENV_VAR_NAME = "RAKSHA_SAFE_ZONES_PATH"

# Simple in-memory cache so we don't re-read/re-parse the file on every
# single request. reload_safe_zones() or passing force_reload=True bypasses it.
_cache = {"path": None, "zones": None}


def _resolve_path(path=None):
    if path:
        return path
    return os.environ.get(ENV_VAR_NAME, _DEFAULT_PATH)


def _parse_feature(feature, index):
    """Convert one GeoJSON Feature into our internal shelter dict, or None
    if the feature is malformed (logged, not fatal -- one bad shelter
    shouldn't take down the whole system during a live incident)."""
    try:
        geometry = feature.get("geometry", {})
        if geometry.get("type") != "Point":
            print(f"[safe_zones_loader] Skipping feature {index}: not a Point geometry.")
            return None

        lon, lat = geometry["coordinates"][0], geometry["coordinates"][1]
        properties = feature.get("properties", {}) or {}

        shelter_id = properties.get("shelter_id") or properties.get("id")
        if not shelter_id:
            shelter_id = f"SZ_AUTO_{index}"
            print(f"[safe_zones_loader] Feature {index} had no shelter_id/id; assigned '{shelter_id}'.")

        shelter = {
            "shelter_id": str(shelter_id),
            "name": properties.get("name", str(shelter_id)),
            "latitude": float(lat),
            "longitude": float(lon),
        }

        # Pass through any extra properties (capacity, type, etc.) without
        # assuming what the GIS/risk teams will eventually include.
        for key, value in properties.items():
            if key not in shelter:
                shelter[key] = value

        return shelter

    except (KeyError, IndexError, TypeError, ValueError) as exc:
        print(f"[safe_zones_loader] Skipping malformed feature {index}: {exc}")
        return None


def load_safe_zones(path=None, force_reload=False):
    """
    Load and return the list of safe zones (shelters) from the GeoJSON file.

    Args:
        path (str, optional): override path to a GeoJSON file. Defaults to
            data/safe_zones.geojson next to this module, or the
            RAKSHA_SAFE_ZONES_PATH environment variable if set.
        force_reload (bool): bypass the in-memory cache and re-read the file
            from disk (use this if the GIS teammate just updated the file).

    Returns:
        list[dict]: each dict has at least shelter_id, name, latitude,
        longitude, plus any extra properties from the GeoJSON file.

    Raises:
        FileNotFoundError: if the resolved path does not exist.
        ValueError: if the file exists but contains no usable Point features.
    """
    resolved_path = _resolve_path(path)

    if not force_reload and _cache["zones"] is not None and _cache["path"] == resolved_path:
        return _cache["zones"]

    if not os.path.exists(resolved_path):
        raise FileNotFoundError(
            f"Safe zones file not found at '{resolved_path}'. "
            f"Either add data/safe_zones.geojson, or set the "
            f"{ENV_VAR_NAME} environment variable to the correct path."
        )

    with open(resolved_path, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    features = geojson.get("features", [])
    zones = [z for z in (_parse_feature(f, i) for i, f in enumerate(features)) if z is not None]

    if not zones:
        raise ValueError(f"No valid Point features found in '{resolved_path}'.")

    _cache["path"] = resolved_path
    _cache["zones"] = zones
    return zones


def reload_safe_zones(path=None):
    """Force a fresh read from disk, e.g. after the GIS teammate pushes an
    updated safe_zones.geojson. Convenience wrapper over force_reload=True."""
    return load_safe_zones(path=path, force_reload=True)
