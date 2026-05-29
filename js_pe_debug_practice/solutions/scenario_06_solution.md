# Scenario 06 Solution - Slow Order Latency

## Commands you should run

- `grep -Rni "O6006" logs/`
- `grep -Rni "latency_ms\\|backlog\\|queue\\|state=down" logs/`
- `less logs/gateway.log`
- `less logs/system.log`
- `tail -n 100 logs/system.log`

## Log lines that matter

- `gateway.log`: queue depth spike then delayed ACK (`latency_ms=920`)
- `system.log`: gateway queue backlog high and worker process marked `state=down`
- `risk.log`: fast processing once request arrives (`processing_ms=8`)

## First divergence

Before risk decision: queueing delay in gateway path introduces most latency.

## Likely root cause

Operational degradation (backlog + degraded worker pool) causes slow order handling; business logic is not the bottleneck.

## Interview explanation

"I decomposed total latency by stage. Risk is fast, so delay accumulates earlier at gateway queueing. System logs confirm backlog and worker instability. I’d treat this as capacity/reliability issue: restore worker health, drain backlog, and alert on queue depth before SLA breach."
