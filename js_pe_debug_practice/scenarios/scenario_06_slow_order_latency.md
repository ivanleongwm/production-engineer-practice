# Scenario 06 - Slow Order Latency

## Incident report

Trader says: "Order O6006 eventually filled, but ACK took almost a second. Desk says system is slow."

## Goal

Determine whether slowness is from business logic or operational pressure (queue/process health).

## Suggested commands to try (no answer)

- `grep -Rni "O6006" logs/`
- `grep -Rni "latency\\|queue\\|backlog\\|state=down" logs/`
- `less logs/gateway.log`
- `less logs/system.log`
- `tail -n 80 logs/system.log`

## Your notes

- expected behavior:
- actual behavior:
- correlation key:
- system path:
- first divergence:
- hypothesis:
- verification:
- fix:
- prevention:
