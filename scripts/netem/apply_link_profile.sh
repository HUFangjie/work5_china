#!/usr/bin/env bash
set -euo pipefail
IFACE=${1:-eth0}
BASE=${2:-20}
JITTER=${3:-5}
LOSS=${4:-1}
sudo tc qdisc replace dev "$IFACE" root netem delay "${BASE}ms" "${JITTER}ms" loss "${LOSS}%"
echo "applied netem on $IFACE"
