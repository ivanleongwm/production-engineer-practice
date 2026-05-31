# Scenario 14 - DB Connection Pool Exhaustion

## Incident report

Order `O1414` (TSLA, 300 shares) was intermittently rejected with `DOWNSTREAM_TIMEOUT`. DBA confirms Postgres is healthy.

## Goal

Distinguish database outage from application-side connection pool exhaustion.

## Suggested commands to try (no answer)

- `grep -Rni "O1414" logs/`
- `grep -Rni "pool_active\|pool_max\|pool_timeout\|connection_pool" logs/`
- `grep -Rni "postgres\|db" logs/system.log`
- `less logs/risk.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
