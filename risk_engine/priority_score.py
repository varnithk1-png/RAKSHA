#Priority score currently uses synthetic/demo accessibility data.

import pandas as pd

INPUT_FILE = "data/risk_zones.csv"
OUTPUT_FILE = "data/final_priority_scores.csv"


def calculate_priority(row):
    risk = row["risk_score"]
    accessibility = row["accessibility"]

    # If routing data is not available, priority cannot be calculated
    if pd.isna(accessibility):
        return None

    # Poor accessibility increases evacuation priority
    priority = (0.7 * risk) + (0.3 * (100 - accessibility))

    return round(priority, 2)


def priority_level(score):

    if pd.isna(score):
        return "Unknown"
    elif score <= 40:
        return "Low Priority"
    elif score <= 60:
        return "Moderate Priority"
    elif score <= 80:
        return "High Priority"
    else:
        return "Critical Priority"


df = pd.read_csv(INPUT_FILE)

df["priority_score"] = df.apply(calculate_priority, axis=1)
df["priority_level"] = df["priority_score"].apply(priority_level)

df.to_csv(OUTPUT_FILE, index=False)

print("Priority scores created successfully!")
print("Total buildings:", len(df))
print("Saved to:", OUTPUT_FILE)

print("\nPriority level distribution:")
print(df["priority_level"].value_counts())

print("\nTop priority buildings:")

top_priority = df.sort_values(
    "priority_score",
    ascending=False,
    na_position="last"
).head(10)

print(
    top_priority[
        [
            "building_id",
            "risk_score",
            "risk_level",
            "accessibility",
            "priority_score",
            "priority_level"
        ]
    ].to_string(index=False)
)