"""Découpage d'une ligne de log HDFS en champs structurés."""
import re
from typing import Iterator, Optional, Tuple

LINE_RE = re.compile(
    r"^(?P<date>\d{6}) (?P<time>\d{6}) (?P<pid>\d+) "
    r"(?P<level>[A-Z]+) (?P<component>[\w.$]+): (?P<content>.*)$"
)
BLOCK_RE = re.compile(r"blk_-?\d+")


def split_line(line: str) -> Optional[dict]:
    """Retourne les champs d'une ligne, ou None si le format n'est pas reconnu."""
    m = LINE_RE.match(line.rstrip("\r\n"))
    if m is None:
        return None
    fields = m.groupdict()
    fields["pid"] = int(fields["pid"])
    fields["block_ids"] = BLOCK_RE.findall(fields["content"])
    return fields


def read_lines(path, limit: Optional[int] = None) -> Iterator[Tuple[int, str]]:
    """Lit un fichier ligne par ligne : renvoie (numéro de ligne à partir de 1, texte)."""
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, start=1):
            if limit is not None and i > limit:
                break
            yield i, line