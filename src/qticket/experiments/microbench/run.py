from __future__ import annotations

from pathlib import Path


from qticket.common.ids import new_id
from qticket.common.logging import JsonlLogger
from qticket.common.time import now_iso
from qticket.crypto.primitives import stage_costs
from qticket.eval.plots import plot_microbench
from qticket.eval.tables import write_overhead_table
from qticket.metrics.record import write_csv
from qticket.schemes.registry import create_scheme


def run_microbench(default_cfg: dict, exp_cfg: dict, scheme_cfg: dict, out_base: Path) -> None:
    logger = JsonlLogger(out_base / 'raw' / 'events.jsonl')
    scheme = create_scheme(scheme_cfg['name'], scheme_cfg)
    costs = stage_costs(scheme_cfg)
    rows = []
    for _ in range(exp_cfg['rounds']):
        event = {
            'ts': now_iso(), 'event_type': 'microbench', 'session_id': new_id('sess'), 'scheme': scheme.name,
            **costs,
            'msg_bytes': scheme_cfg.get('msg_bytes', 500), 'rtt': scheme_cfg.get('rtt', 1),
            'cpu_pct': 10.0, 'mem_mb': 128.0,
        }
        logger.log(event)
        rows.append(event)
    records = write_csv(rows, out_base / 'derived' / 'microbench.csv')
    plot_microbench(records, out_base / 'figures')
    write_overhead_table(records, out_base / 'tables')
