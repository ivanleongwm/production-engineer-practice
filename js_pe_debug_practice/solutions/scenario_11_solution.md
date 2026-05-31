# Scenario 11 Solution - Queue Consumer Lag

## Short answer / root cause

Fill and publish paths are fast. **Position service consumer is lagging** on queue `exec.reports.v2` (~842 messages, ~18.5s lag). Producer (execution publisher) is not the bottleneck.

## Commands to run

```bash
grep -Rni "O1111\|E71111\|trace_id=T-O1111" logs/
grep -Rni "consumer_lag\|lag_messages\|lag_ms\|poll_slow" logs/
grep -Rni "execution_published\|position_update\|late_fill" logs/
grep -h "O1111" logs/* | sort
less logs/position.log
```

## Important log lines to notice

- `gateway.log`: `ack_to_client ... latency_ms=105` — fast ACK
- `engine.log`: `fill_generated ... exec_id=E71111` at ~10:11:01.120
- `execution_publisher.log`: `execution_published ... latency_ms=4` — fast publish
- `system.log`: `consumer_lag queue=exec.reports.v2 lag_messages=842 lag_ms=18500`
- `position.log`: `position_update ... consume_lag_ms=18535` — late consume
- `client.log`: `late_fill_observed waited_ms=18380`

## Red herrings to ignore

- Engine or publisher heartbeat warnings on unrelated partitions
- `slow_ack` patterns from other scenarios — here ACK is fast, fill is late
- Queue depth on gateway_to_risk — different queue entirely

## First divergence

At **position consumer lag** — message published quickly but consumed ~18s later.

## Immediate mitigation

- Scale position consumer instances or increase partition consumption parallelism
- Drain/lag alert on `exec.reports.v2` consumer group
- Temporary manual position reconcile for affected client if needed

## Long-term fix

- Autoscale consumers on lag_ms threshold
- Separate hot/cold consumer pools; dead-letter slow poison messages
- End-to-end latency SLO broken down by stage: ack vs publish vs consume

## 60-second interview explanation

"Client got fast ACK but late fill on O1111. Tracing E71111: engine fill and execution_published both happen within milliseconds. Position update arrives 18 seconds later with consume_lag_ms=18535, and system.log shows consumer_lag 842 messages. First divergence is position consumer lag, not engine or publisher. I'd scale consumers and alert on queue lag, plus track per-stage latency so we don't misblame the matching engine."
