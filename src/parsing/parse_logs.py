"""Parsing d'un fichier de logs complet, par blocs, vers des fichiers Parquet."""
import argparse
import time
from itertools import islice
from pathlib import Path

from src.parsing.drain_parser import build_miner, get_templates, parse_lines
from src.parsing.line_parser import read_lines

ROOT = Path(__file__).resolve().parents[2]


def chunked(iterable, size):
    it = iter(iterable)
    while chunk := list(islice(it, size)):
        yield chunk


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", default=str(ROOT / "data" / "raw" / "HDFS.log"))
    p.add_argument("--config", default=str(ROOT / "configs" / "drain3.ini"))
    p.add_argument("--output", default=str(ROOT / "data" / "processed" / "hdfs_parsed"))
    p.add_argument("--templates", default=str(ROOT / "data" / "processed" / "hdfs_templates.csv"))
    p.add_argument("--state", default=str(ROOT / "state" / "drain3_state.bin"))
    p.add_argument("--limit", type=int, default=None, help="ne traiter que les N premières lignes")
    p.add_argument("--chunk-size", type=int, default=500_000)
    a = p.parse_args()

    out = Path(a.output)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("part-*.parquet"):
        old.unlink()
    state = Path(a.state)
    state.parent.mkdir(parents=True, exist_ok=True)
    state.unlink(missing_ok=True)              # on repart toujours d'un état vierge
    templates_path = Path(a.templates)
    templates_path.parent.mkdir(parents=True, exist_ok=True)

    miner = build_miner(a.config, state)
    t0, total, bad_total = time.time(), 0, 0
    for k, chunk in enumerate(chunked(read_lines(a.input, a.limit), a.chunk_size)):
        df, bad = parse_lines(chunk, miner)
        df.to_parquet(out / f"part-{k:04d}.parquet", index=False)
        total += len(chunk)
        bad_total += bad
        print(f"[{time.time() - t0:7.0f}s] {total:,} lignes | "
              f"{bad_total} mal formées | {len(miner.drain.clusters)} templates", flush=True)

    miner.save_state("fin du parsing")
    templates = get_templates(miner)
    templates.to_csv(templates_path, index=False)
    print(f"Terminé en {time.time() - t0:.0f}s : {total:,} lignes, "
          f"{bad_total} mal formées, {len(templates)} templates.")


if __name__ == "__main__":
    main()