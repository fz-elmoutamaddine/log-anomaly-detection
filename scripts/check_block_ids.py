import pandas as pd
df = pd.read_parquet("data/processed/hdfs_parsed")
m = df[df["block_ids"].map(len) > 1]
print(m["event_id"].value_counts().head())
print(m["block_ids"].map(lambda b: len(set(b))).value_counts())