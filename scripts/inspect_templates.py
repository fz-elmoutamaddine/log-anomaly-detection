import difflib
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
t = pd.read_csv(ROOT / "data" / "processed" / "hdfs_templates.csv")
t = t.sort_values("size", ascending=False).reset_index(drop=True)
total = t["size"].sum()

pd.set_option("display.max_colwidth", 170)
pd.set_option("display.width", 260)
t["part_%"] = (t["size"] / total * 100).round(4)

print(f"{len(t)} templates, {total:,} lignes\n")
print(t[["event_id", "size", "part_%", "template"]].to_string(index=False))

print("\n=== Paires de templates très proches (similarité >= 0.8) ===")
rows = t[["event_id", "template", "size"]].values.tolist()
found = 0
for i in range(len(rows)):
    for j in range(i + 1, len(rows)):
        r = difflib.SequenceMatcher(None, rows[i][1], rows[j][1]).ratio()
        if r >= 0.8:
            found += 1
            print(f"\n[{r:.2f}] event {rows[i][0]} ({rows[i][2]} lignes)  vs  event {rows[j][0]} ({rows[j][2]} lignes)")
            print("   ", rows[i][1])
            print("   ", rows[j][1])
print(f"\n{found} paire(s) proche(s)")