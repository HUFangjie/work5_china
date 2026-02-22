# qticket

轨交车地通信可插拔认证/重绑定方案评测原型。

## 1. 环境准备

```bash
cd /workspace/work5_china
pip install -e . --no-build-isolation
```

> 如你的环境可联网，也可以直接 `pip install -e .`。

## 2. 启动节点（可选）

### 2.1 Docker Compose

```bash
docker compose -f scripts/docker/docker-compose.yml up -d
```

### 2.2 本机多终端

```bash
python -m qticket.cli run-node --role anchor --port 8001
python -m qticket.cli run-node --role ag --id ag1 --port 8002
python -m qticket.cli run-node --role ag --id ag2 --port 8003
python -m qticket.cli run-node --role tg --port 8004
```

健康检查示例：

```bash
curl http://127.0.0.1:8001/health
```

## 3. 运行实验

### 3.1 单方案

```bash
python -m qticket.cli run-exp --exp exp_handover_latency --scheme ours_qticket
```

### 3.2 多方案对比

```bash
python -m qticket.cli run-exp --exp exp_handover_latency --schemes \
  ours_qticket baseline_full_reauth baseline_token_only baseline_ticket_2rtt baseline_qkd_vpn
```

### 3.3 其他实验

```bash
python -m qticket.cli run-exp --exp exp_attack_success --schemes ours_qticket baseline_token_only
python -m qticket.cli run-exp --exp exp_revocation --schemes ours_qticket baseline_full_reauth
python -m qticket.cli run-exp --exp exp_microbench --schemes ours_qticket baseline_qkd_vpn
```

## 4. 如何查看输出数据

每次运行会自动在 `outputs/{experiment}/{scheme}/{timestamp}/` 下生成：

- `raw/events.jsonl`：原始结构化日志
- `derived/*.csv`：派生统计（事件级/汇总级）
- `figures/*.png|*.pdf`：图
- `tables/table_overhead.csv`：开销表

快速查看：

```bash
find outputs -maxdepth 5 -type d
head -n 5 outputs/exp_handover_latency/ours_qticket/<timestamp>/raw/events.jsonl
head -n 5 outputs/exp_handover_latency/ours_qticket/<timestamp>/derived/handover_summary.csv
```

> 在 PyCharm 中，可直接右键 `outputs` 目录 -> `Open in Files`，或双击 CSV / JSONL / PNG / PDF 查看。

## 5. netem（可选）

```bash
bash scripts/netem/apply_link_profile.sh eth0 20 5 1
bash scripts/netem/reset.sh eth0
```
