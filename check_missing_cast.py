
import pandas as pd
from pathlib import Path

data_dir = Path(__file__).resolve().parent / "data"

csv_cast = pd.read_csv(data_dir / "normalized_cast.csv", dtype=str)
mysql_cast = pd.read_csv(data_dir / "mysql_cast_export.csv", dtype=str)

# Normalize column names and text values
for df in (csv_cast, mysql_cast):
    df.columns = df.columns.str.strip().str.lower()
    for col in ["show_id", "actor"]:
        df[col] = df[col].fillna("").str.strip()

# Compare (show_id, actor) pairs
csv_pairs = set(map(tuple, csv_cast[["show_id", "actor"]].values))
mysql_pairs = set(map(tuple, mysql_cast[["show_id", "actor"]].values))

missing = sorted(csv_pairs - mysql_pairs)

print("CSV unique records:", len(csv_pairs))
print("MySQL unique records:", len(mysql_pairs))
print("Missing records:", len(missing))
print("\nRecords missing from MySQL:")

for show_id, actor in missing:
    print(show_id, "|", actor)

if missing:
    pd.DataFrame(missing, columns=["show_id", "actor"]).to_csv(
        data_dir / "missing_cast_records.csv", index=False
    )
    print("\nSaved to data/missing_cast_records.csv")
