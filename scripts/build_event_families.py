"""Regroupe les templates de Drain en familles d'événements (29 attendues pour HDFS)."""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
t = pd.read_csv(ROOT / "data" / "processed" / "hdfs_templates.csv").sort_values("event_id")

FAMILY_RULES = [
    ("writeBlock_exception", r"^writeBlock <BLK> received exception"),
    ("PacketResponder_exception", r"^PacketResponder <BLK> <NUM> Exception"),
    ("receiveBlock_exception", r"^Exception in receiveBlock for block <BLK>"),
]


def family_name(template: str) -> str:
    for name, pattern in FAMILY_RULES:
        if re.match(pattern, template):
            return name
    return template          # tous les autres événements restent seuls


t["family_name"] = t["template"].map(family_name)
order = {name: i + 1 for i, name in enumerate(t["family_name"].drop_duplicates())}
t["family_id"] = t["family_name"].map(order)

print(len(t), "templates ->", t["family_id"].nunique(), "familles")
summary = t.groupby("family_id").agg(
    n_templates=("event_id", "size"), lignes=("size", "sum"), nom=("family_name", "first")
)
pd.set_option("display.max_colwidth", 80)
pd.set_option("display.width", 200)
print(summary.to_string())

out = ROOT / "reports" / "hdfs_event_families.csv"
t[["event_id", "family_id", "family_name", "size", "template"]].to_csv(out, index=False)
print("écrit :", out)