import csv

file_path = "data/clean_buildings.csv"

with open(file_path, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

print("Total buildings:", len(rows))

print("\nColumns available:")
for column in reader.fieldnames:
    print(column)

print("\nFirst building:")
for key, value in rows[0].items():
    print(key, ":", value)

print("\nMissing values:")
for column in reader.fieldnames:
    missing = sum(1 for row in rows if row[column] == "")
    print(column, ":", missing)