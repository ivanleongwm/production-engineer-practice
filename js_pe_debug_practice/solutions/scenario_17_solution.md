# Scenario 17 Solution - Disk Full / Persistence Failure

## Short answer / root cause

**Disk 100% full** on `exec-pub-host-1` (`/var/log/exec-publisher`). Execution publisher process is **alive** but **cannot write outbox** (`no_space_left_on_device`), so fill `E71717` never publishes despite engine generating it.

## Commands to run

```bash
grep -Rni "O1717\|E71717" logs/
grep -Rni "no_space_left\|disk_full\|write_failed\|usage_pct=100" logs/
grep -Rni "publish_skipped\|heartbeat" logs/execution_publisher.log
less logs/system.log
```

## Important log lines to notice

- `engine.log`: `fill_generated exec_id=E71717` — fill exists
- `system.log`: `disk_full mount=/var/log/exec-publisher usage_pct=100 avail_bytes=0`
- `execution_publisher.log`: `write_failed reason=no_space_left_on_device path=.../E71717.json`
- `execution_publisher.log`: `publish_skipped reason=outbox_write_failed`
- `execution_publisher.log`: `heartbeat status=up note=process_alive_but_persist_failing`
- `client.log`: `pending_execution waited_ms=900`

## Red herrings to ignore

- Process heartbeat/up — liveness ≠ ability to persist
- Kafka broker_election warnings on noise orders
- Gateway/risk path healthy — failure is downstream publish

## First divergence

At **outbox write failure on full disk** — after engine fill, before publish.

## Immediate mitigation

- Free disk space (rotate logs, expand volume, delete stale outbox)
- Replay unpublished exec reports from engine once disk cleared
- Fail health check when disk > 90% so LB stops sending traffic

## Long-term fix

- Disk usage alerts; log rotation with size caps
- Separate data volume from log volume
- Outbox replay tooling and idempotent republish by exec_id

## 60-second interview explanation

"O1717 was ACK'd and engine filled E71717, but client never got execution. Publisher heartbeat says up, yet write_failed with no_space_left_on_device and disk_full at 100% on exec-pub-host-1. Publish was skipped. First divergence is disk full blocking persistence, not process death. I'd free disk, replay the exec report, and add disk alerts plus readiness checks that fail when outbox can't write."
