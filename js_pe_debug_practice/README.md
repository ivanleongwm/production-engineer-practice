# Production Engineer Debug Practice (Trading System)

This repository is a deterministic Python-based debugging lab for Production Engineer interview practice — designed to feel closer to real trading-system incident investigation.

It simulates a multi-service trading flow:

- `client` -> `gateway` -> `risk` -> `matching engine` -> `execution publisher` -> `position service`
- plus `system` health/noise logs

You investigate incidents by correlating logs across components, filtering noise, and finding the **first divergence** from the expected path.

## Repository Layout

```
js_pe_debug_practice/
├── README.md
├── INTERVIEW_COMMANDS.md      # grep/find/less cheat sheet
├── generate_logs.py
├── logs/                      # generated log files (overwritten each run)
├── scenarios/                 # incident prompts (no answers)
│   ├── README_RCA_TEMPLATE.md
│   ├── scenario_01_happy_path.md
│   ├── ...
│   └── scenario_20_vendor_timeout.md
└── solutions/                 # detailed walkthroughs
    ├── scenario_01_solution.md
    ├── ...
    └── scenario_20_solution.md
```

## Prerequisites

- Python 3 (standard library only — no pip install needed)

```bash
python --version
```

## How to Run

All commands assume you are in `js_pe_debug_practice/`:

```bash
cd js_pe_debug_practice
```

### Generate a specific scenario (deterministic)

```bash
python generate_logs.py --scenario 11
python generate_logs.py --scenario 11 --difficulty hard
```

Scenarios **1–20** are supported. Each `--scenario N` run is deterministic for a given difficulty.

### Difficulty levels

```bash
python generate_logs.py --scenario 11 --difficulty easy    # ~100–200 lines, clearer signals
python generate_logs.py --scenario 11 --difficulty medium  # ~300–500 lines (default)
python generate_logs.py --scenario 11 --difficulty hard    # ~600–1000 lines, heavy noise
```

Default difficulty is **medium** if omitted.

### Random blind practice

```bash
python generate_logs.py --random
python generate_logs.py --random --difficulty medium
```

Picks a scenario **without revealing the number**. Use this to simulate interview conditions.

### Answer key (concise — not the full solution)

```bash
python generate_logs.py --scenario 11 --answer-key
```

Prints only: scenario number, title, root cause category, and affected order/client/symbol. Compare with `solutions/` after your RCA.

### What gets generated

| File | Component |
|------|-----------|
| `logs/client.log` | Order sender |
| `logs/gateway.log` | Order routing and ACKs |
| `logs/risk.log` | Risk accept/reject decisions |
| `logs/engine.log` | Matching engine fills |
| `logs/execution_publisher.log` | Execution report publishing |
| `logs/position.log` | Position updates |
| `logs/system.log` | DNS, firewall, deploy, health, disk, LB, NTP |

Log lines use grep-friendly structured fields: `ts=`, `level=`, `service=`, `host=`, `order_id=`, `trace_id=`, `exec_id=`, etc.

## Scenarios

| # | Level | File | Incident type | Key correlation ID |
|---|-------|------|---------------|-------------------|
| 1 | Beginner | `scenario_01_happy_path.md` | Baseline happy path | O1001 |
| 2 | Beginner | `scenario_02_risk_reject.md` | Risk rejection | O2002 |
| 3 | Beginner | `scenario_03_gateway_timeout.md` | Downstream timeout | O3003 |
| 4 | Beginner | `scenario_04_missing_execution_report.md` | Missing execution report | O4004 |
| 5 | Beginner | `scenario_05_duplicate_fill_position_wrong.md` | Duplicate fill / wrong position | O5005 / E5505 |
| 6 | Beginner | `scenario_06_slow_order_latency.md` | Slow latency / queue backlog | O6006 |
| 7 | Intermediate | `scenario_07_dns_service_discovery.md` | Stale DNS / service discovery | O7007 |
| 8 | Intermediate | `scenario_08_firewall_port_blocked.md` | Firewall blocks port | O8008 |
| 9 | Intermediate | `scenario_09_process_down.md` | Process crash / not listening | O9009 |
| 10 | Intermediate | `scenario_10_bad_deploy_config.md` | Bad deploy / config mismatch | O1010 / 9988.HK |
| 11 | Intermediate | `scenario_11_queue_consumer_lag.md` | Queue consumer lag | O1111 / E71111 |
| 12 | Intermediate | `scenario_12_duplicate_idempotency.md` | Duplicate message / idempotency | O1212 / E71212 |
| 13 | Hard | `scenario_13_gc_latency.md` | GC pause / memory pressure | O1313 |
| 14 | Hard | `scenario_14_db_pool_exhaustion.md` | DB connection pool exhausted | O1414 |
| 15 | Hard | `scenario_15_exchange_disconnect.md` | Exchange FIX session disconnect | O1515 |
| 16 | Hard | `scenario_16_clock_skew.md` | Clock skew / misleading timestamps | O1616 |
| 17 | Hard | `scenario_17_disk_full.md` | Disk full / persistence failure | O1717 / E71717 |
| 18 | Hard | `scenario_18_permission_auth.md` | Permission / auth issue | O1818 / C1818 |
| 19 | Hard | `scenario_19_partial_outage_lb.md` | Bad instance behind load balancer | O1919 |
| 20 | Hard | `scenario_20_vendor_timeout.md` | External vendor API slow | O2020 |

**Beginner (1–6):** shorter paths, fewer red herrings at medium difficulty.  
**Intermediate/Hard (7–20):** realistic noise, misleading warnings, unrelated orders, and cross-layer failures.

Open the matching scenario file for the incident report. Use `scenarios/README_RCA_TEMPLATE.md` for your write-up. Do **not** open the solution until finished.

See also: [INTERVIEW_COMMANDS.md](INTERVIEW_COMMANDS.md)

## 20-Minute Timed Routine

Set a timer. Goal: isolate the **failing layer**, not memorize every scenario.

1. **Read scenario prompt** (2 min) — note order ID, client, symbol, user complaint
2. **Search correlation IDs** (3 min) — `grep -Rni "Oxxxx" logs/` and `trace_id=`
3. **Check ERROR/WARN** (3 min) — `grep -Rni "ERROR\|WARN" logs/` then filter to your order
4. **Build expected path** (3 min) — write the happy path: client → gateway → risk → engine → publisher → position
5. **Find first divergence** (4 min) — earliest step where actual ≠ expected; cite log line
6. **Write RCA** (3 min) — use `scenarios/README_RCA_TEMPLATE.md`
7. **Compare solution** (2 min) — `less solutions/scenario_XX_solution.md`

Repeat at `--difficulty hard` once medium feels comfortable.

## First Investigation Flow

```bash
find logs/ -type f
grep -Rni "ORDER_ID_FROM_PROMPT" logs/
grep -Rni "ERROR\|WARN" logs/
less logs/gateway.log
less logs/system.log
```

Replace `ORDER_ID_FROM_PROMPT` with the order ID from your scenario file.

## What You Practice

- Cross-log correlation with `grep -Rni`
- Distinguishing **symptoms** (timeout, reject) from **root cause layer** (DNS, firewall, pool, skew)
- Filtering noise: unrelated orders, health checks, misleading errors
- Building an **expected path** and finding **first divergence**
- Interview-friendly 60-second root-cause storytelling

## Interview Mindset

In Production Engineer interviews, the goal is **not** to know every failure mode upfront. It is to:

1. Ask what the user expected vs what happened
2. Pick a correlation key and trace the request
3. Identify which **layer** broke (network, process, config, queue, external dep)
4. Explain evidence, red herrings, mitigation, and prevention clearly

Use exactly one of `--scenario` or `--random` — not both (unless using `--answer-key`, which requires `--scenario`).

## Notes

- Deterministic: same scenario number + difficulty → same logs
- Standard library only, no external dependencies
- Logs include intentional noise at medium/hard difficulty
- Scenarios 1–6 preserved; 7–20 extend the lab
