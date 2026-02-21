from __future__ import annotations

import random
from pathlib import Path


from qticket.common.ids import new_id
from qticket.common.logging import JsonlLogger
from qticket.common.time import now_iso
from qticket.eval.plots import plot_attack
from qticket.eval.tables import write_overhead_table
from qticket.metrics.record import write_csv
from qticket.schemes.registry import create_scheme


def run_attack_success(default_cfg: dict, exp_cfg: dict, scheme_cfg: dict, out_base: Path) -> None:
    random.seed(default_cfg.get('seed', 7))
    logger = JsonlLogger(out_base / 'raw' / 'events.jsonl')
    scheme = create_scheme(scheme_cfg['name'], scheme_cfg)
    scheme.bootstrap({})
    rt = scheme.issue_rt(default_cfg['train_id'])
    st = scheme.issue_st(default_cfg['train_id'], rt, 'ag1')
    rows = []
    for atk in exp_cfg['attack_types']:
        for _ in range(exp_cfg['rounds'] // len(exp_cfg['attack_types'])):
            opts = {atk: True}
            res = scheme.rebind(default_cfg['train_id'], st, 'ag2', opts)
            event = {
                'ts': now_iso(), 'event_type': 'attack', 'session_id': new_id('sess'), 'scheme': scheme.name,
                'attack_type': atk, 'accepted': res.accepted, 'result': 'accept' if res.accepted else 'reject',
                'error_code': res.error_code, 'msg_bytes': res.msg_bytes, 'rtt': res.rtt,
                'cpu_pct': 10.0, 'mem_mb': 128.0,
            }
            logger.log(event)
            rows.append(event)
    records = write_csv(rows, out_base / 'derived' / 'attack_events.csv')
    plot_attack(records, out_base / 'figures')
    write_overhead_table(records, out_base / 'tables')
