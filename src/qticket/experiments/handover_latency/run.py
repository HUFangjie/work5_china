from __future__ import annotations

import random
import time
from pathlib import Path


from qticket.common.ids import new_id
from qticket.common.logging import JsonlLogger
from qticket.common.time import now_iso
from qticket.metrics.record import write_csv
from qticket.metrics.stats import pct
from qticket.eval.plots import plot_handover
from qticket.eval.tables import write_overhead_table
from qticket.schemes.registry import create_scheme


def run_handover_latency(default_cfg: dict, exp_cfg: dict, scheme_cfg: dict, out_base: Path) -> None:
    random.seed(default_cfg.get('seed', 7))
    logger = JsonlLogger(out_base / 'raw' / 'events.jsonl')
    scheme = create_scheme(scheme_cfg['name'], scheme_cfg)
    scheme.bootstrap({})
    rt = scheme.issue_rt(default_cfg['train_id'])
    st = scheme.issue_st(default_cfg['train_id'], rt, 'ag1')
    rows = []
    for freq in exp_cfg['switch_frequencies_hz']:
        for profile in exp_cfg['profiles']:
            net = default_cfg['network_profiles'][profile]
            for _ in range(exp_cfg['rounds'] // len(exp_cfg['switch_frequencies_hz'])):
                sid = new_id('sess')
                link_ctx = random.choice(['ag1', 'ag2'])
                res = scheme.rebind(default_cfg['train_id'], st, link_ctx, {})
                latency = net['base_ms'] * res.rtt + net['jitter_ms'] + (1.0 / freq)
                event = {
                    'ts': now_iso(), 'event_type': 'handover', 'session_id': sid, 'scheme': scheme.name,
                    'switch_freq_hz': freq, 'profile': profile, 'result': 'accept' if res.accepted else 'reject',
                    'error_code': res.error_code, 'latency_ms': latency, 'msg_bytes': res.msg_bytes, 'rtt': res.rtt,
                    'cpu_pct': 10.0, 'mem_mb': 128.0,
                    'verify_ticket_ms': scheme_cfg.get('verify_cost_ms', 1.0),
                    'revocation_lookup_ms': scheme_cfg.get('revocation_lookup_ms', 0.5),
                    'challenge_response_ms': scheme_cfg.get('challenge_cost_ms', 1.0),
                    'kdf_ms': 0.2, 'restore_tunnel_ms': scheme_cfg.get('vpn_rebuild_ms', 2.0),
                }
                logger.log(event)
                rows.append(event)
                if res.new_st:
                    st = res.new_st
                time.sleep(0.001)
    records = write_csv(rows, out_base / 'derived' / 'handover_events.csv')
    latencies=[r['latency_ms'] for r in records]
    summary = [{'scheme': scheme.name, 'p50_ms': pct(latencies, 50), 'p95_ms': pct(latencies, 95), 'p99_ms': pct(latencies, 99)}]
    write_csv(summary, out_base / 'derived' / 'handover_summary.csv')
    plot_handover(records, out_base / 'figures')
    write_overhead_table(records, out_base / 'tables')
