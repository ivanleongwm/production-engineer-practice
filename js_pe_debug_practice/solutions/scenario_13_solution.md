# Scenario 13 Solution - Latency Spike / GC Pressure

## Short answer / root cause

**Gateway memory (RSS) grew to ~1040MB** with **major GC pauses (~412ms)** just before order `O1313`. ACK latency (~455ms) aligns with GC timestamp — not risk reject or exchange issue.

## Commands to run

```bash
grep -Rni "O1313" logs/
grep -Rni "gc_pause\|rss_mb\|rss_sample" logs/system.log logs/gateway.log
grep -Rni "slow_ack\|latency_ms" logs/gateway.log logs/client.log
less logs/system.log
```

## Important log lines to notice

- `system.log`: rising `rss_sample` 512 → 1040 MB on gateway-host-1
- `gateway.log`: `gc_pause pause_ms=412 gc_type=major rss_mb=1040` just before order path
- `gateway.log`: `ack_to_client latency_ms=455` for O1313
- `risk.log`: `risk_eval latency_ms=6` — risk is fast
- `client.log`: `slow_ack_observed ack_latency_ms=455`

## Red herrings to ignore

- Gateway queue backlog warnings on unrelated noise orders
- Risk p95 latency alerts from other scenarios
- Intermittent md-feed stale quote errors — non-order path

## First divergence

At **gateway GC pause** immediately preceding elevated call_risk/ack latency for O1313.

## Immediate mitigation

- Restart gateway instance to clear heap / relieve memory pressure
- Shed load or rate-limit ingress temporarily
- Route traffic to healthy gateway instance if clustered

## Long-term fix

- Fix memory leak; tune GC heap limits and pause targets
- Alert on RSS trend + GC pause p99
- Separate latency metrics: queue wait vs GC vs downstream

## 60-second interview explanation

"O1313 had a 455ms ACK with no reject. Risk eval took 6ms. Gateway logs show a 412ms major GC pause at 1040MB RSS, and system.log shows RSS climbing over time. Latency spike aligns with GC, not risk or engine. First divergence is gateway memory/GC. I'd restart the affected instance, investigate the leak, and alert on RSS plus GC pause correlation with ack latency."
