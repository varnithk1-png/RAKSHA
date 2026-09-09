import pandas as pd

INPUT_FILE = "data/final_priority_scores.csv"

df = pd.read_csv(INPUT_FILE)

print("========== RISK ENGINE VALIDATION ==========")

# 1. Basic information
print("\n1. BASIC INFORMATION")
print("Total buildings:", len(df))
print("Total columns:", len(df.columns))

# 2. Duplicate building IDs
print("\n2. DUPLICATE BUILDING IDs")
duplicates = df["building_id"].duplicated().sum()
print("Duplicate IDs:", duplicates)

# 3. Missing values
print("\n3. MISSING VALUES")
missing = df.isnull().sum()
print(missing[missing > 0])

# 4. Coordinate validation
print("\n4. COORDINATE VALIDATION")

invalid_latitude = (
    (df["latitude"] < -90) |
    (df["latitude"] > 90)
).sum()

invalid_longitude = (
    (df["longitude"] < -180) |
    (df["longitude"] > 180)
).sum()

print("Invalid latitude values:", invalid_latitude)
print("Invalid longitude values:", invalid_longitude)

# 5. Risk score validation
print("\n5. RISK SCORE VALIDATION")

invalid_risk = (
    (df["risk_score"] < 0) |
    (df["risk_score"] > 100)
).sum()

print("Risk scores outside 0-100:", invalid_risk)

# 6. Accessibility validation
print("\n6. ACCESSIBILITY VALIDATION")

invalid_accessibility = (
    (df["accessibility"].notna()) &
    (
        (df["accessibility"] < 0) |
        (df["accessibility"] > 100)
    )
).sum()

print("Accessibility scores outside 0-100:", invalid_accessibility)

# 7. Priority score validation
print("\n7. PRIORITY SCORE VALIDATION")

invalid_priority = (
    (df["priority_score"].notna()) &
    (
        (df["priority_score"] < 0) |
        (df["priority_score"] > 100)
    )
).sum()

print("Priority scores outside 0-100:", invalid_priority)

# 8. Risk level distribution
print("\n8. RISK LEVEL DISTRIBUTION")
print(df["risk_level"].value_counts())

# 9. Priority level distribution
print("\n9. PRIORITY LEVEL DISTRIBUTION")
print(df["priority_level"].value_counts())

# 10. Final status
print("\n========== VALIDATION COMPLETE ==========")

if (
    duplicates == 0
    and invalid_latitude == 0
    and invalid_longitude == 0
    and invalid_risk == 0
    and invalid_accessibility == 0
    and invalid_priority == 0
):
    print("STATUS: PASS")
else:
    print("STATUS: CHECK REQUIRED")