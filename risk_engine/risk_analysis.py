#Analysis is based on the current MVP risk scores(which are demo values).

import pandas as pd


INPUT_FILE = "data/final_risk_scores.csv"


df = pd.read_csv(INPUT_FILE)

print("Total buildings:", len(df))

print("\nRisk level distribution:")

risk_counts = df["risk_level"].value_counts()

for level, count in risk_counts.items():
    percentage = (count / len(df)) * 100
    print(f"{level}: {count} ({percentage:.2f}%)")


print("\nRisk score statistics:")
print(df["risk_score"].describe())


print("\nTop 10 highest-risk buildings:")

top_risk = df.sort_values("risk_score", ascending=False).head(10)

print(
    top_risk[
        [
            "building_id",
            "building_type",
            "latitude",
            "longitude",
            "vulnerability",
            "seismic_hazard",
            "risk_score",
            "risk_level"
        ]
    ].to_string(index=False)
)