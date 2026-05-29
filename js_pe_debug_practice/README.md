# Production Engineer Debug Practice (Trading System)

This repository is a small, deterministic Python-based debugging lab for Production Engineer interview practice.

It simulates a multi-service trading flow:

- `client` -> `gateway` -> `risk` -> `matching engine` -> `execution publisher` -> `position service`
- plus `system` health/noise logs

You investigate incidents by correlating logs across components and finding the first divergence.

## Repository Layout

- `generate_logs.py` - creates logs for a chosen scenario
- `logs/` - generated log files for each service
- `scenarios/` - incident prompts (no answers)
- `solutions/` - walkthroughs and expected debugging approach

## Quick Start

From this directory:

```bash
python generate_logs.py --scenario 3
```

Or generate a blind random case:

```bash
python generate_logs.py --random
```

The script overwrites all files in `logs/`.

## 30-Minute Practice Routine

1. Generate a scenario:
   - `python generate_logs.py --random`
2. Inspect files:
   - `find . -maxdepth 3 -type f`
3. Pick an order/correlation key and trace it:
   - `grep -Rni "O2003" logs/`
4. Open full logs for context:
   - `less logs/gateway.log`
   - `less logs/system.log`
5. Identify the first divergence in expected service path.
6. Write your root-cause analysis in the scenario template.
7. Compare with the matching file in `solutions/`.

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

- Deterministic by default (`--scenario N`).
- Standard library only, no external dependencies.
- Logs intentionally include noisy `INFO`/`WARN`/`ERROR` lines so you must filter effectively.
