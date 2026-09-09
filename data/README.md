# GIS & Spatial Data Layer (Task 3)

## Dataset Summary
- **Study Area**: Hyderabad, Telangana, India[cite: 1, 2]
- **Base Geospatial Data**: OpenStreetMap / Overture Maps schema[cite: 1, 2]
- **Observed Data**: Geographic coordinates based on real Hyderabad location features[cite: 1, 2].
- **Synthetic/Demo Data**: Simulated building risk ratings, victim locations, responder units, and route vectors.

## Data Schemas
- `buildings_risk.geojson`: `building_id`, `risk_score`, `risk_level`, `latitude`, `longitude`
- `safe_zones.geojson`: `shelter_id`, `name`, `latitude`, `longitude`, `capacity`[cite: 2]
- `responders_victims.geojson`: `type`, `building_id`, `responder_id`, `latitude`, `longitude`[cite: 2]
- `sample_route.geojson`: `distance_km`, `duration_min`[cite: 2]