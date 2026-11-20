from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_parquet(ROOT / "data" / "processed" / "hdfs_parsed")

print(f"{len(df):,} lignes")
print("templates distincts :", df["event_id"].nunique())
print("période :", df["timestamp"].min(), "→", df["timestamp"].max())
print("line_id unique et complet :", df["line_id"].is_unique, df["line_id"].min(), df["line_id"].max())
n_blocks = df["block_ids"].map(len)
print("lignes sans bloc :", int((n_blocks == 0).sum()))
print("lignes à plusieurs blocs DISTINCTS :", int((n_blocks > 1).sum()))
print(df.loc[n_blocks > 1, "event_id"].value_counts().head(10))
print()
print(df["event_id"].value_counts().sort_index().to_string())