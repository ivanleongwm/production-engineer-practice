# Production Engineer Debug Practice (Trading System)

This repository is a small, deterministic Python-based debugging lab for Production Engineer interview practice.

It simulates a multi-service trading flow:

- `client` -> `gateway` -> `risk` -> `matching engine` -> `execution publisher` -> `position service`
- plus `system` health/noise logs

You investigate incidents by correlating logs across components and finding the first divergence.

## Repository Layout

```
js_pe_debug_practice/
├── README.md
├── generate_logs.py
├── logs/                    # generated log files (overwritten each run)
├── scenarios/               # incident prompts (no answers)
│   ├── scenario_01_happy_path.md
│   ├── scenario_02_risk_reject.md
│   ├── scenario_03_gateway_timeout.md
│   ├── scenario_04_missing_execution_report.md
│   ├── scenario_05_duplicate_fill_position_wrong.md
│   └── scenario_06_slow_order_latency.md
└── solutions/               # walkthroughs and expected debugging approach
    ├── scenario_01_solution.md
    ├── ...
    └── scenario_06_solution.md
```

## Prerequisites

- Python 3 (standard library only — no pip install needed)

Check Python is available:

```powershell
python --version
```

If `python` is not recognized on Windows, try:

```powershell
py --version
```

## How to Run

All commands below assume you are in the `js_pe_debug_practice/` directory. From the parent workspace:

```powershell
cd js_pe_debug_practice
```

### Generate a specific scenario (deterministic)

Pick a scenario number from 1 to 6:

```powershell
python generate_logs.py --scenario 3
```

On Windows, if `python` fails:

```powershell
py generate_logs.py --scenario 3
```

This overwrites all files in `logs/` with logs for that scenario.

### Generate a random scenario (blind practice)

The script picks a scenario without telling you which one:

```powershell
python generate_logs.py --random
```

Use this when you want to simulate a real interview where you don't know the root cause upfront.

### What gets generated

Each run writes these log files:

| File | Component |
|------|-----------|
| `logs/client.log` | Order sender |
| `logs/gateway.log` | Order routing and ACKs |
| `logs/risk.log` | Risk accept/reject decisions |
| `logs/engine.log` | Matching engine fills |
| `logs/execution_publisher.log` | Execution report publishing |
| `logs/position.log` | Position updates |
| `logs/system.log` | Process health, queues, connectivity |

## Scenarios

| # | File | Incident type |
|---|------|---------------|
| 1 | `scenario_01_happy_path.md` | Baseline happy path |
| 2 | `scenario_02_risk_reject.md` | Risk rejection |
| 3 | `scenario_03_gateway_timeout.md` | Downstream timeout |
| 4 | `scenario_04_missing_execution_report.md` | Missing execution report |
| 5 | `scenario_05_duplicate_fill_position_wrong.md` | Duplicate fill, wrong position |
| 6 | `scenario_06_slow_order_latency.md` | Slow latency / queue backlog |

Open the matching scenario file for the incident report and a blank RCA template. Do **not** open the solution until you've finished your analysis.

## 30-Minute Practice Routine

1. **Generate a scenario**
   ```powershell
   python generate_logs.py --random
   ```
2. **Inspect files**
   ```bash
   find . -maxdepth 3 -type f
   ```
3. **Pick an order ID from the incident report and trace it**
   ```bash
   grep -Rni "O3003" logs/
   ```
4. **Open full logs for context**
   ```bash
   less logs/gateway.log
   less logs/system.log
   ```
5. **Identify the first divergence** in the expected service path.
6. **Write your root-cause analysis** in the scenario template (expected vs actual behavior, correlation key, hypothesis, fix).
7. **Compare with the solution**
   ```bash
   less solutions/scenario_03_solution.md
   ```

## First Investigation Flow

After generating logs, run these commands in order:

```bash
# 1. See what files exist
find logs/ -type f

# 2. Search for the order ID from the incident report
grep -Rni "O3003" logs/

# 3. Filter for errors and warnings only
grep -Rni "ERROR\|WARN" logs/

# 4. Read the gateway log (usually the best starting point)
less logs/gateway.log

# 5. Check system health for queue/process issues
grep -Rni "queue\|backlog\|state=down\|latency" logs/system.log
```

Replace `O3003` with the order ID from whichever scenario you are practising.

## What You Practice

- `grep -Rni` for cross-log correlation
- `find` for structure and discovery
- `less` and `/pattern` navigation in large files
- `tail -n` and `tail -f` for live-style reasoning
- `ps`-style process reasoning from `system.log`
- interview-friendly root-cause storytelling

## Common Issue Families Included

- risk rejection
- downstream timeout
- missing execution report
- duplicate fill causing wrong position
- slow latency due to queue backlog
- service/process down signal in system logs
- bad symbol mapping noise
- timestamp/timezone confusion noise

## Notes

- Deterministic by default (`--scenario N` always produces the same logs).
- Standard library only, no external dependencies.
- Logs intentionally include noisy `INFO`/`WARN`/`ERROR` lines so you must filter effectively.
- Use exactly one of `--scenario` or `--random` — not both.
