from __future__ import annotations

import subprocess


def tc_apply(interface: str, profile: dict) -> None:
    cmd = (
        f"tc qdisc replace dev {interface} root netem delay {profile['base_ms']}ms "
        f"{profile['jitter_ms']}ms loss {profile['loss']*100}%"
    )
    subprocess.run(cmd, shell=True, check=False)


def tc_reset(interface: str) -> None:
    subprocess.run(f"tc qdisc del dev {interface} root", shell=True, check=False)
