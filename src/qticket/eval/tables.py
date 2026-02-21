from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


def write_overhead_table(rows, table_dir: Path) -> None:
    table_dir.mkdir(parents=True, exist_ok=True)
    agg = defaultdict(lambda: {'n': 0, 'msg_bytes': 0.0, 'rtt': 0.0, 'cpu_pct': 0.0, 'mem_mb': 0.0})
    for r in rows:
        s = r['scheme']
        agg[s]['n'] += 1
        for k in ['msg_bytes', 'rtt', 'cpu_pct', 'mem_mb']:
            agg[s][k] += float(r.get(k, 0.0))
    out_rows = []
    for s, v in agg.items():
        n = max(v['n'], 1)
        out_rows.append({
            'scheme': s,
            'msg_bytes': v['msg_bytes'] / n,
            'rounds': v['n'],
            'handshake_rtt': v['rtt'] / n,
            'cpu_pct': v['cpu_pct'] / n,
            'mem_mb': v['mem_mb'] / n,
        })
    with (table_dir / 'table_overhead.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()) if out_rows else ['scheme'])
        w.writeheader()
        if out_rows:
            w.writerows(out_rows)
