# Routing input is currently DEMO/SYNTHETIC data.
# Replace with actual routing results during integration.


import pandas as pd


ROUTING_FILE = "data/sample_routing.csv"
OUTPUT_FILE = "data/routing_with_accessibility.csv"


def calculate_accessibility(distance_km, duration_min):

    # Start with maximum accessibility
    score = 100

    # Penalize longer distance
    if distance_km > 5:
        score -= 40
    elif distance_km > 3:
        score -= 25
    elif distance_km > 1:
        score -= 10

    # Penalize longer travel time
    if duration_min > 15:
        score -= 30
    elif duration_min > 10:
        score -= 20
    elif duration_min > 5:
        score -= 10

    return max(score, 0)


df = pd.read_csv(ROUTING_FILE)

df["accessibility"] = df.apply(
    lambda row: calculate_accessibility(
        row["distance_km"],
        row["duration_min"]
    ),
    axis=1
)

df.to_csv(OUTPUT_FILE, index=False)

print("Accessibility scores created successfully!")
print("Total routes:", len(df))
print("Saved to:", OUTPUT_FILE)