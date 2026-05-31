# Scenario 14 Solution - DB Connection Pool Exhaustion

## Short answer / root cause

Postgres is **healthy**, but **risk service connection pool is exhausted** (`pool_active=32 pool_max=32 pool_idle=0`, 14 waiting threads). Risk waits 2.5s for a DB connection and gateway times out — **app-side pool starvation**, not DB down.

## Commands to run

```bash
grep -Rni "O1414" logs/
grep -Rni "pool_active\|pool_max\|pool_idle\|pool_timeout\|connection_pool" logs/
grep -Rni "postgres\|healthcheck" logs/system.log
grep -Rni "risk_timeout\|DOWNSTREAM_TIMEOUT" logs/gateway.log
less logs/risk.log
```

## Important log lines to notice

- `system.log`: `postgres-monitor ... status=healthy connections=42 max_connections=200`
- `risk.log`: `pool_wait pool_active=32 pool_max=32 pool_idle=0`
- `risk.log`: `pool_timeout reason=connection_pool_exhausted waited_ms=2500`
- `gateway.log`: `risk_timeout waited_ms=2520 reason=downstream_timeout`
- `system.log`: `waiting_threads=14` on pool metrics

## Red herrings to ignore

- DOWNSTREAM_TIMEOUT at gateway — symptom, not root cause
- Generic risk slow queries on unrelated orders
- Postgres healthy metric — rules out DB outage but not pool config

## First divergence

At **risk DB pool wait** — cannot acquire connection within timeout while DB server is up.

## Immediate mitigation

- Increase pool size temporarily / restart risk to release leaked connections
- Kill long-running risk queries holding connections
- Circuit-break new orders if pool wait exceeds threshold

## Long-term fix

- Fix connection leaks; right-size pool vs Postgres max_connections
- Separate read replica pool for heavy analytics queries
- Metrics: pool wait time, idle count, active count, waiting threads

## 60-second interview explanation

"O1414 got DOWNSTREAM_TIMEOUT at gateway, but postgres-monitor shows DB healthy. Risk logs show pool exhausted — all 32 connections active, zero idle, pool_timeout after 2500ms with 14 waiting threads. First divergence is app connection pool, not database outage. I'd restart risk to free connections, fix leaks, resize the pool, and alert on idle=0 with waiting threads."
