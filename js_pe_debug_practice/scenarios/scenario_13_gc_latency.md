# Scenario 13 - Latency Spike / GC Pressure

## Incident report

Client `C1313` reports intermittent slow ACKs on order `O1313` (META, 80 shares). No rejects. Latency spikes to ~450ms occasionally.

## Goal

Correlate latency spikes with process resource metrics (memory/GC).

## Suggested commands to try (no answer)

- `grep -Rni "O1313" logs/`
- `grep -Rni "gc_pause\|rss_mb\|slow_ack" logs/`
- `grep -Rni "latency_ms" logs/gateway.log`
- `less logs/system.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
