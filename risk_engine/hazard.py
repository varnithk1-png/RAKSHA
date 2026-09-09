#demo values

import pandas as pd


INPUT_FILE = "data/buildings_with_vulnerability.csv"
OUTPUT_FILE = "data/buildings_with_hazard.csv"


# Hyderabad seismic hazard input for MVP
# Zone II -> low to moderate seismic hazard
SEISMIC_ZONE = "Zone II"
HAZARD_SCORE = 20


df = pd.read_csv(INPUT_FILE)

df["seismic_zone"] = SEISMIC_ZONE
df["seismic_hazard"] = HAZARD_SCORE

df.to_csv(OUTPUT_FILE, index=False)

print("Seismic hazard added successfully!")
print("Seismic zone:", SEISMIC_ZONE)
print("Hazard score:", HAZARD_SCORE)
print("Total buildings:", len(df))
print("Saved to:", OUTPUT_FILE)