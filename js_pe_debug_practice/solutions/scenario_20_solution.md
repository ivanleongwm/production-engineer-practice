# Scenario 20 Solution - Dependency Timeout / Vendor API Slow

## Short answer / root cause

Gateway **reference-data enrichment** calls **`refdata-vendor-api`** for uncached **`BRK.B`**. Vendor is slow; gateway retries then **times out at 4000ms** (`REFDATA_TIMEOUT`). **Cached symbol AAPL** (`cache_hit=true`) passes immediately on O2021.

## Commands to run

```bash
grep -Rni "O2020\|O2021" logs/
grep -Rni "vendor_timeout\|vendor_lookup\|refdata\|cache_hit" logs/
grep -Rni "REFDATA_TIMEOUT" logs/gateway.log
less logs/gateway.log
```

## Important log lines to notice

- `gateway.log`: `vendor_lookup_start symbol=BRK.B cache_hit=false vendor=refdata-vendor-api`
- `gateway.log`: `vendor_retry attempt=1 backoff_ms=500`
- `gateway.log`: `vendor_timeout waited_ms=4000 threshold_ms=4000`
- `gateway.log`: `reject_to_client reason=REFDATA_TIMEOUT` for O2020
- `gateway.log`: O2021 AAPL `cache_hit=true` → `order_routed latency_ms=18`

## Red herrings to ignore

- Risk or engine errors — order never reaches them
- md-feed stale quote on XYZ — different data path
- Assuming all symbols broken — only uncached/slow vendor lookups fail

## First divergence

At **vendor API wait exceeding threshold** during refdata lookup for BRK.B — before risk routing.

## Immediate mitigation

- Fail over to backup refdata vendor or read-only cache snapshot
- Extend timeout temporarily (with cap) or bypass enrichment for vetted symbols
- Pre-warm cache for actively traded symbols like BRK.B

## Long-term fix

- Circuit breaker on vendor API with cached fallback
- Async enrichment where possible; stale-cache-allowed policy per symbol
- Vendor SLO monitoring and alert on p95 lookup latency

## 60-second interview explanation

"O2020 on BRK.B failed REFDATA_TIMEOUT. Gateway never routed to risk — it waited on refdata-vendor-api with cache_hit=false, retried once, then timed out at 4s. O2021 AAPL with cache_hit=true routed in 18ms. First divergence is external vendor latency on uncached symbols, not internal trading stack. I'd serve from cache fallback, pre-warm BRK.B, add vendor circuit breakers, and monitor vendor p95 separately from gateway latency."
