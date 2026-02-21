from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict


def parse_jsonl(path: Path) -> List[Dict]:
    rows = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows
