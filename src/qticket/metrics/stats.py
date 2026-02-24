from __future__ import annotations


def pct(values, q: float) -> float:
    if not values:
        return 0.0
    vals = sorted(float(v) for v in values)
    k = (len(vals) - 1) * q / 100.0
    f = int(k)
    c = min(f + 1, len(vals) - 1)
    if f == c:
        return vals[f]
    return vals[f] + (vals[c] - vals[f]) * (k - f)
