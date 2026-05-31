# Scenario 12 Solution - Duplicate Message / Idempotency

## Short answer / root cause

Execution publisher **retried publish** for the same **`exec_id=E71212`** after `no_ack_from_broker`. Position service applied the execution **twice** because it lacks **idempotency by exec_id** (`idempotency_key=none`).

## Commands to run

```bash
grep -Rni "O1212\|E71212" logs/
grep -Rni "duplicate\|retry\|idempotency\|publish_retry" logs/
grep -Rni "position_update" logs/position.log | grep E71212
less logs/execution_publisher.log
less logs/position.log
```

## Important log lines to notice

- `execution_publisher.log`: first `execution_published attempt=1`
- `execution_publisher.log`: `publish_retry reason=no_ack_from_broker attempt=2`
- `execution_publisher.log`: second `execution_published attempt=2` same exec_id
- `position.log`: two `position_update` lines for `exec_id=E71212` — delta 60 twice, position 160 → 220
- `position.log`: second update `reason=duplicate_exec_applied idempotency_key=none`

## Red herrings to ignore

- Single fill in engine — only one real fill; duplicate is downstream
- Client duplicate warnings on unrelated orders
- Kafka broker_election noise — not the duplicate apply root cause

## First divergence

At **second position_update for same exec_id** after publisher retry — consumer should dedupe.

## Immediate mitigation

- Manual position correction for client C1212 / AMZN
- Stop consumer briefly and replay from offset only after idempotency fix (careful ops)
- Disable publisher retry-to-same-topic without dedupe key (short term)

## Long-term fix

- Idempotent consumer: store processed exec_ids (DB unique constraint or cache)
- Publisher idempotency keys; broker dedupe window
- Reconciliation job detecting duplicate exec_id applies

## 60-second interview explanation

"Position is 60 shares high for O1212. Engine shows one fill E71212. Publisher logged a retry after no_ack_from_broker and published the same exec_id twice. Position service applied both updates — idempotency_key=none and duplicate_exec_applied on the second. First divergence is missing consumer idempotency, not a double fill at the engine. I'd fix the position, then enforce exec_id dedupe at the consumer and idempotent publish semantics."
