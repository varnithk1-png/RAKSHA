#Accessibility values currently come from synthetic/demo routing data.

import pandas as pd

RISK_FILE = "data/final_risk_scores.csv"
ACCESSIBILITY_FILE = "data/routing_with_accessibility.csv"
OUTPUT_FILE = "data/final_risk_with_accessibility.csv"

risk_df = pd.read_csv(RISK_FILE)
accessibility_df = pd.read_csv(ACCESSIBILITY_FILE)

combined_df = risk_df.merge(
    accessibility_df,
    on="building_id",
    how="left"
)

combined_df.to_csv(OUTPUT_FILE, index=False)

print("Risk and accessibility data combined successfully!")
print("Total buildings:", len(combined_df))
print("Saved to:", OUTPUT_FILE)

print("\nColumns:")
print(combined_df.columns.tolist())

print("\nSample:")
print(
    combined_df[
        [
            "building_id",
            "risk_score",
            "risk_level",
            "distance_km",
            "duration_min",
            "accessibility"
        ]
    ].head(10).to_string(index=False)
)