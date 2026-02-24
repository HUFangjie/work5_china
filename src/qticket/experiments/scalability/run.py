from __future__ import annotations

import random
import time
from collections import defaultdict
from pathlib import Path

from qticket.common.ids import new_id
from qticket.common.logging import JsonlLogger
from qticket.common.time import now_iso
from qticket.eval.plots import plot_scalability
from qticket.eval.tables import write_overhead_table, write_scalability_capacity_table
from qticket.metrics.record import write_csv
from qticket.metrics.stats import pct
from qticket.schemes.registry import create_scheme


def run_scalability(default_cfg: dict, exp_cfg: dict, scheme_cfg: dict, out_base: Path) -> None:
    random.seed(default_cfg.get("seed", 7))
    logger = JsonlLogger(out_base / "raw" / "events.jsonl")

    scheme = create_scheme(scheme_cfg["name"], scheme_cfg)
    scheme.bootstrap({})
    rt = scheme.issue_rt(default_cfg["train_id"])
    st = scheme.issue_st(default_cfg["train_id"], rt, "ag1")

    anchor_capacity_qps = float(exp_cfg.get("anchor_capacity_qps", 120.0))
    rounds_per_point = int(exp_cfg.get("rounds_per_point", 60))

    rows = []
    for profile in exp_cfg["profiles"]:
        net = default_cfg["network_profiles"][profile]
        for num_trains in exp_cfg["num_trains"]:
            for handover_rate in exp_cfg["handover_rates_hz"]:
                offered_qps = float(num_trains) * float(handover_rate)
                overload_ratio = max(0.0, offered_qps / anchor_capacity_qps - 1.0)

                for _ in range(rounds_per_point):
                    sid = new_id("sess")
                    link_ctx = random.choice(["ag1", "ag2"])
                    res = scheme.rebind(default_cfg["train_id"], st, link_ctx, {})

                    # queue_delay grows superlinearly once overloaded
                    queue_delay_ms = (overload_ratio ** 1.5) * 25.0
                    service_ms = net["base_ms"] * res.rtt + net["jitter_ms"]
                    latency_ms = service_ms + queue_delay_ms + random.random() * 0.8

                    drop_rate = min(0.95, overload_ratio * 0.25 + net.get("loss", 0.0))
                    dropped = random.random() < drop_rate
                    accepted = bool(res.accepted) and (not dropped)
                    error_code = "ERR_DROPPED" if dropped else res.error_code

                    ag_cpu = min(100.0, 20.0 + offered_qps * 0.35 + overload_ratio * 25.0)
                    anchor_cpu = min(100.0, 15.0 + offered_qps * 0.45 + overload_ratio * 30.0)

                    event = {
                        "ts": now_iso(),
                        "event_type": "scalability",
                        "session_id": sid,
                        "scheme": scheme.name,
                        "profile": profile,
                        "num_trains": int(num_trains),
                        "handover_rate": float(handover_rate),
                        "offered_qps": offered_qps,
                        "accepted": int(accepted),
                        "result": "accept" if accepted else "reject",
                        "error_code": error_code,
                        "latency_ms": latency_ms,
                        "queue_delay_ms": queue_delay_ms,
                        "drop_rate": drop_rate,
                        "ag_cpu_pct": ag_cpu,
                        "anchor_cpu_pct": anchor_cpu,
                        "msg_bytes": res.msg_bytes,
                        "rtt": res.rtt,
                        "cpu_pct": ag_cpu,
                        "mem_mb": 128.0,
                    }
                    logger.log(event)
                    rows.append(event)
                    if res.new_st:
                        st = res.new_st
                    time.sleep(0.0005)

    records = write_csv(rows, out_base / "derived" / "scalability_events.csv")

    buckets = defaultdict(list)
    for r in records:
        key = (r["scheme"], r["profile"], r["num_trains"], r["handover_rate"])
        buckets[key].append(r)

    summary = []
    for (scheme_name, profile, num_trains, handover_rate), grp in buckets.items():
        latencies = [float(x["latency_ms"]) for x in grp]
        accepted = [int(x["accepted"]) for x in grp]
        qps = float(num_trains) * float(handover_rate)
        success_rate = sum(accepted) / len(accepted)
        throughput = qps * success_rate
        summary.append(
            {
                "scheme": scheme_name,
                "profile": profile,
                "num_trains": int(num_trains),
                "handover_rate": float(handover_rate),
                "rebind_success_rate": success_rate,
                "latency_p95_ms": pct(latencies, 95),
                "latency_p99_ms": pct(latencies, 99),
                "ag_cpu_pct": sum(float(x["ag_cpu_pct"]) for x in grp) / len(grp),
                "anchor_cpu_pct": sum(float(x["anchor_cpu_pct"]) for x in grp) / len(grp),
                "qps": qps,
                "throughput_rps": throughput,
                "queue_delay_ms": sum(float(x["queue_delay_ms"]) for x in grp) / len(grp),
                "drop_rate": sum(float(x["drop_rate"]) for x in grp) / len(grp),
            }
        )

    summary_records = write_csv(summary, out_base / "derived" / "scalability_summary.csv")

    plot_scalability(summary_records, out_base / "figures")
    write_overhead_table(records, out_base / "tables")
    write_scalability_capacity_table(summary_records, out_base / "tables")
