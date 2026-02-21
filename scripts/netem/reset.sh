#!/usr/bin/env bash
set -euo pipefail
IFACE=${1:-eth0}
sudo tc qdisc del dev "$IFACE" root || true
echo "reset netem on $IFACE"
