# Scenario 05 - Duplicate Fill, Wrong Position

## Incident report

Trader reports: "Position jumped too much after order O5005. Looks like fill counted twice."

## Goal

Prove whether duplicate execution handling failed and where idempotency broke.

## Suggested commands to try (no answer)

- `grep -Rni "O5005\\|E5505" logs/`
- `grep -Rni "duplicate\\|idempotency\\|position_update" logs/`
- `less logs/execution_publisher.log`
- `less logs/position.log`
- `grep -Rni "anomaly\\|ERROR" logs/position.log`

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
