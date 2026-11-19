import hashlib
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"            # adapter si HDFS.log est dans un sous-dossier
LOG = RAW / "HDFS.log"
LABELS = RAW / "preprocessed" / "anomaly_label.csv"


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def count_lines(path):
    with open(path, "rb") as f:
        return sum(1 for _ in f)


print("Lignes de HDFS.log :", f"{count_lines(LOG):,}")
print("SHA256 de HDFS.log :", sha256(LOG))

df = pd.read_csv(LABELS)
print("Colonnes :", list(df.columns))
print(df["Label"].value_counts())
print("Blocs :", f"{len(df):,}", "| anomalies :", round((df["Label"] == "Anomaly").mean() * 100, 2), "%")