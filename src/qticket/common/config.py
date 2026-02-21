from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _parse_scalar(v: str) -> Any:
    v = v.strip()
    if v in {"true", "True"}:
        return True
    if v in {"false", "False"}:
        return False
    if v.startswith("[") or v.startswith("{"):
        return ast.literal_eval(v)
    try:
        if "." in v:
            return float(v)
        return int(v)
    except ValueError:
        return v.strip('"').strip("'")


def load_yaml(path: str | Path) -> Dict[str, Any]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    root: Dict[str, Any] = {}
    stack: List[Tuple[int, Dict[str, Any]]] = [(-1, root)]
    for raw in lines:
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, val = line.strip().split(":", 1)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        cur = stack[-1][1]
        if val.strip() == "":
            cur[key] = {}
            stack.append((indent, cur[key]))
        else:
            cur[key] = _parse_scalar(val)
    return root


def load_default_config(root: Path) -> Dict[str, Any]:
    return load_yaml(root / "configs" / "default.yaml")
