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


def write_scalability_capacity_table(summary_rows, table_dir: Path) -> None:
    table_dir.mkdir(parents=True, exist_ok=True)
    # max throughput under CPU<80 constraint
    best = {}
    for r in summary_rows:
        if float(r.get('ag_cpu_pct', 0)) >= 80.0 or float(r.get('anchor_cpu_pct', 0)) >= 80.0:
            continue
        s = r['scheme']
        tp = float(r.get('throughput_rps', 0.0))
        if s not in best or tp > best[s]['max_rebind_per_s_under_cpu80']:
            best[s] = {
                'scheme': s,
                'max_rebind_per_s_under_cpu80': tp,
                'num_trains': int(r.get('num_trains', 0)),
                'handover_rate': float(r.get('handover_rate', 0.0)),
                'profile': r.get('profile', ''),
            }
    import csv
    out = list(best.values())
    with (table_dir / 'table_cpu80_capacity.csv').open('w', encoding='utf-8', newline='') as f:
        fields = ['scheme', 'max_rebind_per_s_under_cpu80', 'num_trains', 'handover_rate', 'profile']
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in out:
            w.writerow(row)
