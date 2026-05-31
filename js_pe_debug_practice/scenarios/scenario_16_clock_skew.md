# Scenario 16 - Clock Skew / Misleading Timestamps

## Incident report

On-call engineer flagged order `O1616` (MSFT): matching engine log appears to show `order_received` *before* gateway sent the order. Is the engine processing orders out of order?

## Goal

Determine whether timestamps reflect true ordering or host clock skew.

## Suggested commands to try (no answer)

- `grep -Rni "O1616" logs/`
- `grep -Rni "clock_offset\|ntp\|host_clock_skew\|seq=" logs/`
- `grep -h "O1616" logs/* | sort`
- `less logs/system.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
