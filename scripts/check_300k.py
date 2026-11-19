import sys
from itertools import islice
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.parsing.drain_parser import build_miner, get_templates, parse_lines

LOG = ROOT / "data" / "raw" / "HDFS.log"
N = 300_000

with open(LOG, encoding="utf-8", errors="replace") as f:
    lines = list(enumerate(islice(f, N), start=1))

miner = build_miner(ROOT / "configs" / "drain3.ini")
df, bad = parse_lines(lines, miner)
t = get_templates(miner)

print(f"{len(df):,} lignes parsées | {bad} mal formées | {len(t)} templates")
print("Templates contenant INTERRUPTED :", int(t["template"].str.contains("INTERRUPTED").sum()))
print()

pd.set_option("display.max_colwidth", 140)
pd.set_option("display.width", 200)
print(t.sort_values("size").to_string(index=False))