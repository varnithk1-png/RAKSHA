import json
import random
import os

os.makedirs('data', exist_ok=True)

# Generate live victims & responders
victims = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [78.4772 + random.uniform(-0.05, 0.05), 17.4065 + random.uniform(-0.05, 0.05)]},
            "properties": {"type": "victim", "victim_id": f"V-{100+i}", "urgency": "High"}
        } for i in range(5)
    ] + [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [78.4772 + random.uniform(-0.04, 0.04), 17.4065 + random.uniform(-0.04, 0.04)]},
            "properties": {"type": "responder", "name": f"Unit-{i+1}"}
        } for i in range(3)
    ]
}

with open('data/live_victims.json', 'w') as f:
    json.dump(victims, f, indent=2)

print("Sample data generated successfully.")
