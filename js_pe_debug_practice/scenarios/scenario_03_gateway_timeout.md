# Scenario 03 - Gateway Timeout

## Incident report

Trader says: "Order O3003 was sent but came back as downstream timeout."

## Goal

Trace timing across gateway and risk to prove where timeout happens and whether processing eventually completed anyway.

## Suggested commands to try (no answer)

- `grep -Rni "O3003" logs/`
- `grep -Rni "timeout\\|waited_ms\\|latency" logs/`
- `less logs/gateway.log`
- `less logs/risk.log`
- `grep -Rni "p95_latency\\|threshold" logs/system.log`

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
