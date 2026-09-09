# NOTE: Risk zones are derived from the MVP risk scores.(Real data for a specific location).

import pandas as pd

INPUT_FILE = "data/final_risk_with_accessibility.csv"
OUTPUT_FILE = "data/risk_zones.csv"

df = pd.read_csv(INPUT_FILE)

def classify_zone(score):
    if score <= 30:
        return "Low Risk Zone"
    elif score <= 60:
        return "Moderate Risk Zone"
    elif score <= 80:
        return "High Risk Zone"
    else:
        return "Very High Risk Zone"

df["risk_zone"] = df["risk_score"].apply(classify_zone)

df.to_csv(OUTPUT_FILE, index=False)

print("Risk zones created successfully!")
print("Total buildings:", len(df))
print("Saved to:", OUTPUT_FILE)

print("\nRisk zone distribution:")
print(df["risk_zone"].value_counts())