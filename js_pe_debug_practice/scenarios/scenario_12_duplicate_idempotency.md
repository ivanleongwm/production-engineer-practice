# Scenario 12 - Duplicate Message / Idempotency

## Incident report

Client `C1212` reports position for AMZN is 60 shares too high after order `O1212`. The order itself looked normal — one fill, one ACK.

## Goal

Determine whether the position service double-counted an execution report.

## Suggested commands to try (no answer)

- `grep -Rni "O1212\|E71212" logs/`
- `grep -Rni "duplicate\|retry\|idempotency" logs/`
- `grep -Rni "position_update" logs/position.log`
- `less logs/execution_publisher.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
