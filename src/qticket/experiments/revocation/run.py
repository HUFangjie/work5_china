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

    rounds = int(exp_cfg['rounds'])
    revoke_at = int(rounds * float(exp_cfg.get('revoke_at_ratio', 0.4)))
    propagation_ms = float(scheme_cfg.get('revocation_propagation_ms', 20.0))

    rows = []
    revoke_ts = None
    revoke_enforced = False
    last_post_revoke_accept_elapsed_ms = 0.0
    first_post_revoke_reject_elapsed_ms = None

    for i in range(rounds):
        now = time.time()
        if i == revoke_at:
            revoke_ts = now

        if revoke_ts is not None and (not revoke_enforced):
            elapsed_ms = (now - revoke_ts) * 1000.0
            if elapsed_ms >= propagation_ms:
                ctx['revocations'].revoke(st.st_id, now)
                revoke_enforced = True

        res = scheme.rebind(default_cfg['train_id'], st, random.choice(['ag1', 'ag2']), {})

        elapsed_since_revoke_ms = (now - revoke_ts) * 1000.0 if revoke_ts is not None else 0.0

        if revoke_ts is not None and res.accepted:
            last_post_revoke_accept_elapsed_ms = max(last_post_revoke_accept_elapsed_ms, elapsed_since_revoke_ms)
        if revoke_ts is not None and (not res.accepted) and first_post_revoke_reject_elapsed_ms is None:
            first_post_revoke_reject_elapsed_ms = elapsed_since_revoke_ms

        event = {
            'ts': now_iso(),
            'event_type': 'revocation',
            'session_id': new_id('sess'),
            'scheme': scheme.name,
            'accepted': res.accepted,
            'result': 'accept' if res.accepted else 'reject',
            'error_code': res.error_code,
            # Event-level progress metrics
            'revoke_effect_ms': max(0.0, elapsed_since_revoke_ms),
            'residual_window_ms': max(0.0, elapsed_since_revoke_ms) if (revoke_ts is not None and not revoke_enforced) else 0.0,
            'false_reject': int((revoke_ts is None) and (not res.accepted)),
            'msg_bytes': res.msg_bytes,
            'rtt': res.rtt,
            'cpu_pct': 10.0,
            'mem_mb': 128.0,
        }
        logger.log(event)
        rows.append(event)
        time.sleep(0.001)

    records = write_csv(rows, out_base / 'derived' / 'revocation_events.csv')

    summary = [{
        'scheme': scheme.name,
        'configured_propagation_ms': propagation_ms,
        'observed_revoke_effect_ms': round(first_post_revoke_reject_elapsed_ms or 0.0, 3),
        'observed_residual_window_ms': round(last_post_revoke_accept_elapsed_ms, 3),
        'false_reject_count': sum(int(r['false_reject']) for r in records),
        'false_reject_rate': (sum(int(r['false_reject']) for r in records) / len(records)) if records else 0.0,
    }]
    write_csv(summary, out_base / 'derived' / 'revocation_summary.csv')

    plot_revocation(records, out_base / 'figures')
    write_overhead_table(records, out_base / 'tables')
