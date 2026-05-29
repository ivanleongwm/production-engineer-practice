# Scenario 05 Solution - Duplicate Fill / Wrong Position

## Commands you should run

- `grep -Rni "O5005\\|E5505" logs/`
- `grep -Rni "duplicate\\|retry_without_idempotency_guard" logs/`
- `grep -Rni "position_update\\|anomaly" logs/position.log`
- `less logs/execution_publisher.log`
- `less logs/position.log`

## Log lines that matter

- `execution_publisher.log`: duplicate publish warning for same `exec_id`
- `position.log`: same `exec_id=E5505` applied twice, second update flagged as anomaly
- `client.log`: duplicate execution also observed by client

## First divergence

At execution publisher retry path where idempotency guard is missing.

## Likely root cause

Duplicate execution message accepted and re-applied by position service, inflating position.

## Interview explanation

"I traced by `exec_id` to avoid ambiguity. The same execution is emitted twice and position is incremented twice. First divergence is duplicate publish from retry logic without dedupe. I’d enforce idempotency at publisher and consumer (e.g., processed-exec cache/DB uniqueness)."
