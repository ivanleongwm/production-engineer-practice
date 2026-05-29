# Scenario 01 Solution - Happy Path

## Commands you should run

- `grep -Rni "O1001" logs/`
- `grep -Rni "E5001" logs/`
- `less logs/gateway.log`
- `less logs/engine.log`
- `less logs/position.log`

## Log lines that matter

- `client.log`: order sent, execution received
- `gateway.log`: order received/routed and ACK sent
- `risk.log`: `decision=ACCEPT`
- `engine.log`: `fill_generated`
- `execution_publisher.log`: execution published
- `position.log`: position updated once

## First divergence

None. This is your baseline expected path.

## Likely root cause

No incident; system behaved as designed.

## Interview explanation

"I traced by `order_id` and `exec_id` through each service in sequence. There is no state mismatch, no timing anomaly, and final position update is consistent with the fill. This establishes a known-good baseline to compare failing scenarios."
