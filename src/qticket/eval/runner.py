from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from qticket.common.config import load_default_config, load_yaml
from qticket.common.time import ts_slug
from qticket.experiments.attack_success.run import run_attack_success
from qticket.experiments.handover_latency.run import run_handover_latency
from qticket.experiments.microbench.run import run_microbench
from qticket.experiments.revocation.run import run_revocation

EXPERIMENTS = {
    "exp_handover_latency": run_handover_latency,
    "exp_attack_success": run_attack_success,
    "exp_revocation": run_revocation,
    "exp_microbench": run_microbench,
}


def run_experiment(exp_name: str, schemes: List[str], repo_root: Path) -> Dict[str, Path]:
    if exp_name not in EXPERIMENTS:
        raise KeyError(f"unknown experiment: {exp_name}")
    default_cfg = load_default_config(repo_root)
    exp_cfg = load_yaml(repo_root / "configs" / "experiments" / f"{exp_name}.yaml")
    ts = ts_slug()
    outputs = {}
    for scheme in schemes:
        scheme_cfg = load_yaml(repo_root / "configs" / "schemes" / f"{scheme}.yaml")
        out_base = repo_root / "outputs" / exp_name / scheme / ts
        for sub in ["raw", "derived", "figures", "tables"]:
            (out_base / sub).mkdir(parents=True, exist_ok=True)
        EXPERIMENTS[exp_name](default_cfg, exp_cfg, scheme_cfg, out_base)
        outputs[scheme] = out_base
    return outputs
