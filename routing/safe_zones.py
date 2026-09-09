"""
safe_zones.py
RAKSHA - Task 5: Evacuation & Routing

Lightweight, synthetic/demo safe-zone dataset used for MVP development and
testing. Replace or extend with real study-area data prepared by the
Map/GIS team (Task 3) before final integration.

Each entry:
    shelter_id (str): unique identifier used across the system.
    name (str):        human-readable label shown on the frontend/map.
    latitude (float):  shelter latitude.
    longitude (float): shelter longitude.
    capacity (int):    approximate number of people the shelter can hold.
"""

# Demo / synthetic safe zone dataset.
# NOTE: coordinates are illustrative placeholders for the selected study
# area and are NOT verified real-world shelter locations.
SAFE_ZONES = [
    {"shelter_id": "SZ-01", "name": "Community Hall", "latitude": 17.3850, "longitude": 78.4867, "capacity": 500},
    {"shelter_id": "SZ-02", "name": "School Ground", "latitude": 17.3980, "longitude": 78.4920, "capacity": 1000},
]
