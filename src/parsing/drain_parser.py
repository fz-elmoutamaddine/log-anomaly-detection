"""Parsing de logs avec Drain3."""
import re
from typing import Iterable, Tuple

import pandas as pd
from drain3 import TemplateMiner
from drain3.file_persistence import FilePersistence
from drain3.template_miner_config import TemplateMinerConfig

from src.parsing.line_parser import split_line

COLUMNS = ["line_id", "date", "time", "pid", "level", "component", "event_id", "block_ids"]

# Cas particulier : sans traitement, Drain fusionne ce message avec
# "PacketResponder N for block X terminating" (5 mots sur 6 identiques).
# Les 46 blocs concernés dans HDFS_v1 sont tous étiquetés anormaux.
INTERRUPTED_RE = re.compile(r"PacketResponder \d+ for block blk_-?\d+ Interrupted\.")


def build_miner(config_path, state_path=None, sim_th=None, depth=None) -> TemplateMiner:
    """Crée un parseur Drain. Sans state_path, rien n'est sauvegardé (utile pour les tests)."""
    config = TemplateMinerConfig()
    config.load(str(config_path))
    if sim_th is not None:
        config.drain_sim_th = sim_th
    if depth is not None:
        config.drain_depth = depth
    persistence = FilePersistence(str(state_path)) if state_path else None
    return TemplateMiner(persistence, config)


def parse_lines(lines: Iterable[Tuple[int, str]], miner: TemplateMiner):
    """Parse des (line_id, texte). Retourne (DataFrame, nombre de lignes mal formées)."""
    rows, bad = [], 0
    for line_id, text in lines:
        fields = split_line(text)
        if fields is None:
            bad += 1
            continue
        content = fields["content"]
        if INTERRUPTED_RE.match(content):
            content = "INTERRUPTED " + content     # mot en plus : Drain crée un cluster distinct
        result = miner.add_log_message(content)
        rows.append((
            line_id, fields["date"], fields["time"], fields["pid"],
            fields["level"], fields["component"],
            result["cluster_id"], fields["block_ids"],
        ))
    df = pd.DataFrame(rows, columns=COLUMNS)
    df["timestamp"] = pd.to_datetime(df.pop("date") + df.pop("time"), format="%y%m%d%H%M%S")
    return df, bad


def get_templates(miner: TemplateMiner) -> pd.DataFrame:
    """Dictionnaire final event_id -> template (à lire À LA FIN du parsing)."""
    rows = [(c.cluster_id, c.get_template(), c.size) for c in miner.drain.clusters]
    return pd.DataFrame(rows, columns=["event_id", "template", "size"]).sort_values("event_id")