#not actual data(demo)

import pandas as pd


INPUT_FILE = "data/buildings_with_hazard.csv"
OUTPUT_FILE = "data/buildings_with_exposure.csv"


def calculate_exposure(row):

    score = 20

    building_type = str(row["building_type"]).lower()

    # Buildings likely to have more people
    if building_type == "residential":
        score += 30
    elif building_type in ["commercial", "education"]:
        score += 25
    elif building_type == "medical":
        score += 30
    elif building_type == "civic":
        score += 20

    # More floors → potentially more people exposed
    floors = row["num_floors"]

    if pd.notna(floors):
        if floors >= 6:
            score += 30
        elif floors >= 3:
            score += 20
        else:
            score += 10

    return min(score, 100)


df = pd.read_csv(INPUT_FILE)

df["population_exposure"] = df.apply(
    calculate_exposure,
    axis=1
)

df.to_csv(OUTPUT_FILE, index=False)

print("Population exposure scores created successfully!")
print("Total buildings:", len(df))
print("Saved to:", OUTPUT_FILE)