# Scenario 17 - Disk Full / Persistence Failure

## Incident report

Order `O1717` (NVDA, 120 shares) was ACK'd internally and engine generated fill `E71717`, but client never received execution report. Execution publisher process is still running.

## Goal

Determine why a healthy-looking process failed to publish/persist execution reports.

## Suggested commands to try (no answer)

- `grep -Rni "O1717\|E71717" logs/`
- `grep -Rni "no_space_left\|disk_full\|write_failed" logs/`
- `grep -Rni "publish_skipped\|heartbeat" logs/execution_publisher.log`
- `less logs/system.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
