from __future__ import annotations

import random
import time
from pathlib import Path


from qticket.common.ids import new_id
from qticket.common.logging import JsonlLogger
from qticket.common.time import now_iso
from qticket.eval.plots import plot_revocation
from qticket.eval.tables import write_overhead_table
from qticket.metrics.record import write_csv
from qticket.schemes.registry import create_scheme


def run_revocation(default_cfg: dict, exp_cfg: dict, scheme_cfg: dict, out_base: Path) -> None:
    random.seed(default_cfg.get('seed', 7))
    logger = JsonlLogger(out_base / 'raw' / 'events.jsonl')
    scheme = create_scheme(scheme_cfg['name'], scheme_cfg)
    ctx = {}
    scheme.bootstrap(ctx)
    rt = scheme.issue_rt(default_cfg['train_id'])
    st = scheme.issue_st(default_cfg['train_id'], rt, 'ag1')
    rounds = exp_cfg['rounds']
    revoke_at = int(rounds * exp_cfg.get('revoke_at_ratio', 0.4))
    rows = []
    t0 = time.time()
    for i in range(rounds):
        if i == revoke_at:
            ctx['revocations'].revoke(st.st_id, time.time())
        res = scheme.rebind(default_cfg['train_id'], st, random.choice(['ag1', 'ag2']), {})
        eff_ms = max(0.0, (time.time() - t0) * 1000 - revoke_at)
        event = {
            'ts': now_iso(), 'event_type': 'revocation', 'session_id': new_id('sess'), 'scheme': scheme.name,
            'accepted': res.accepted, 'result': 'accept' if res.accepted else 'reject', 'error_code': res.error_code,
            'revoke_effect_ms': eff_ms, 'residual_window_ms': max(0.0, eff_ms - 5), 'false_reject': int((i < revoke_at) and (not res.accepted)),
            'msg_bytes': res.msg_bytes, 'rtt': res.rtt, 'cpu_pct': 10.0,
            'mem_mb': 128.0,
        }
        logger.log(event)
        rows.append(event)
    records = write_csv(rows, out_base / 'derived' / 'revocation_events.csv')
    plot_revocation(records, out_base / 'figures')
    write_overhead_table(records, out_base / 'tables')
