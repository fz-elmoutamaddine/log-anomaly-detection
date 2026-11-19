import itertools
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.parsing.drain_parser import build_miner, parse_lines
from src.parsing.evaluation import grouping_accuracy
from src.parsing.line_parser import read_lines

LOG = ROOT / "tests" / "data" / "HDFS_2k.log"
TRUTH = ROOT / "tests" / "data" / "HDFS_2k.log_structured.csv"
CONFIG = ROOT / "configs" / "drain3.ini"

truth = pd.read_csv(TRUTH)[["LineId", "EventId"]].rename(columns={"EventId": "event_truth"})
results = []
for sim_th, depth in itertools.product([0.3, 0.4, 0.5, 0.6, 0.7], [3, 4, 5]):
    miner = build_miner(CONFIG, sim_th=sim_th, depth=depth)
    t0 = time.time()
    df, bad = parse_lines(read_lines(LOG), miner)
    elapsed = time.time() - t0
    merged = df.merge(truth, left_on="line_id", right_on="LineId")
    results.append({
        "sim_th": sim_th,
        "depth": depth,
        "n_templates": df["event_id"].nunique(),
        "n_templates_truth": truth["event_truth"].nunique(),
        "grouping_accuracy": round(grouping_accuracy(merged["event_truth"], merged["event_id"]), 4),
        "seconds": round(elapsed, 2),
    })

out = pd.DataFrame(results).sort_values("grouping_accuracy", ascending=False)
print(out.to_string(index=False))
out.to_csv(ROOT / "reports" / "parsing_tuning.csv", index=False)