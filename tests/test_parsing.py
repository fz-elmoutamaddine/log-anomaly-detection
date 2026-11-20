from pathlib import Path

import pandas as pd

from src.parsing.drain_parser import build_miner, parse_lines
from src.parsing.evaluation import grouping_accuracy
from src.parsing.line_parser import read_lines, split_line

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "tests" / "data" / "HDFS_2k.log"
TRUTH = ROOT / "tests" / "data" / "HDFS_2k.log_structured.csv"
CONFIG = ROOT / "configs" / "drain3.ini"

LINE = ("081109 203615 148 INFO dfs.DataNode$PacketResponder: "
        "PacketResponder 1 for block blk_38865049064139660 terminating")


# ---------- découpage d'une ligne ----------

def test_split_line_valid():
    f = split_line(LINE)
    assert f["date"] == "081109" and f["time"] == "203615"
    assert f["pid"] == 148 and f["level"] == "INFO"
    assert f["component"] == "dfs.DataNode$PacketResponder"
    assert f["block_ids"] == ["blk_38865049064139660"]


def test_split_line_invalid_returns_none():
    assert split_line("ceci n'est pas un log HDFS") is None


def test_multiple_blocks_extracted():
    line = ("081109 203615 148 INFO dfs.FSNamesystem: "
            "BLOCK* ask 10.250.19.102:50010 to delete blk_-1 blk_2")
    assert split_line(line)["block_ids"] == ["blk_-1", "blk_2"]


# ---------- masques et regroupement par Drain ----------

def test_same_template_when_only_variables_differ():
    miner = build_miner(CONFIG)
    a = "Receiving block blk_111 src: /10.250.1.1:5000 dest: /10.250.1.2:50010"
    b = "Receiving block blk_-222 src: /10.250.9.9:6000 dest: /10.250.7.7:50010"
    assert miner.add_log_message(a)["cluster_id"] == miner.add_log_message(b)["cluster_id"]


def test_variable_length_block_lists_share_one_template():
    miner = build_miner(CONFIG)
    one = "BLOCK* ask 10.250.1.1:50010 to delete  blk_-111"
    many = "BLOCK* ask 10.250.2.2:50010 to delete  blk_222 blk_-333 blk_444 blk_555"
    assert miner.add_log_message(one)["cluster_id"] == miner.add_log_message(many)["cluster_id"]


def test_ip_lists_with_spaces_share_one_template():
    miner = build_miner(CONFIG)
    one = "BLOCK* ask 10.250.1.1:50010 to replicate blk_1 to datanode(s) 10.250.2.2:50010"
    many = "BLOCK* ask 10.250.3.3:50010 to replicate blk_2 to datanode(s) 10.250.4.4:50010 10.250.5.5:50010"
    assert miner.add_log_message(one)["cluster_id"] == miner.add_log_message(many)["cluster_id"]


def test_ip_lists_with_commas_share_one_template():
    miner = build_miner(CONFIG)
    one = "10.250.1.1:50010 Starting thread to transfer block blk_1 to 10.250.2.2:50010"
    many = "10.250.3.3:50010 Starting thread to transfer block blk_2 to 10.250.4.4:50010, 10.250.5.5:50010"
    assert miner.add_log_message(one)["cluster_id"] == miner.add_log_message(many)["cluster_id"]


# ---------- parsing de l'échantillon ----------

def test_no_malformed_line_in_sample():
    df, bad = parse_lines(read_lines(SAMPLE), build_miner(CONFIG))
    assert bad == 0
    assert len(df) == 2000


def test_parsing_is_deterministic():
    d1, _ = parse_lines(read_lines(SAMPLE), build_miner(CONFIG))
    d2, _ = parse_lines(read_lines(SAMPLE), build_miner(CONFIG))
    assert d1["event_id"].tolist() == d2["event_id"].tolist()


def test_grouping_accuracy_on_sample():
    df, _ = parse_lines(read_lines(SAMPLE), build_miner(CONFIG))
    truth = pd.read_csv(TRUTH)[["LineId", "EventId"]].rename(columns={"EventId": "event_truth"})
    merged = df.merge(truth, left_on="line_id", right_on="LineId")
    assert grouping_accuracy(merged["event_truth"], merged["event_id"]) >= 0.99

def test_interrupted_packet_responder_is_a_separate_event():
    lines = [
        (1, "081109 203615 148 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_1 terminating"),
        (2, "081109 203616 149 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_2 terminating"),
        (3, "081109 203617 150 WARN dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_3 Interrupted."),
    ]
    df, bad = parse_lines(lines, build_miner(CONFIG))
    ids = df["event_id"].tolist()
    assert bad == 0
    assert ids[0] == ids[1]          # deux "terminating" : même événement
    assert ids[2] != ids[0]          # "Interrupted." : événement distinct

def test_duplicate_block_ids_are_removed():
    line = ("081109 203615 148 INFO dfs.FSDataset: Deleting block blk_-5 "
            "file /mnt/hadoop/dfs/data/current/subdir3/blk_-5")
    assert split_line(line)["block_ids"] == ["blk_-5"]