from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping, List, Dict


def write_csv(rows: Iterable[Mapping], path: Path) -> List[Dict]:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return []
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return rows
