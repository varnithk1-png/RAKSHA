#demo values

import pandas as pd


INPUT_FILE = "data/buildings_with_exposure.csv"
OUTPUT_FILE = "data/final_risk_scores.csv"


def calculate_risk(row):

    vulnerability = row["vulnerability"]
    hazard = row["seismic_hazard"]
    exposure = row["population_exposure"]

    # Combine vulnerability, seismic hazard and population exposure
    risk_score = (
        0.5 * vulnerability
        + 0.2 * hazard
        + 0.3 * exposure
    )

    return round(risk_score, 2)


def risk_level(score):

    if score <= 30:
        return "Low"
    elif score <= 60:
        return "Moderate"
    elif score <= 80:
        return "High"
    else:
        return "Very High"


df = pd.read_csv(INPUT_FILE, low_memory=False)
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
df["risk_score"] = df.apply(calculate_risk, axis=1)

df["risk_level"] = df["risk_score"].apply(risk_level)

df.to_csv(OUTPUT_FILE, index=False)

print("Final risk scores created successfully!")
print("Total buildings:", len(df))
print("Saved to:", OUTPUT_FILE)