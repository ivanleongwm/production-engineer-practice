# Scenario 20 - Dependency Timeout / Vendor API Slow

## Incident report

Order `O2020` (BRK.B, 50 shares) was rejected with `REFDATA_TIMEOUT`. Client says AAPL orders work fine from the same session.

## Goal

Isolate whether an external reference-data vendor API is causing enrichment/validation timeouts.

## Suggested commands to try (no answer)

- `grep -Rni "O2020\|O2021" logs/`
- `grep -Rni "vendor_timeout\|refdata\|cache_hit" logs/`
- `grep -Rni "REFDATA_TIMEOUT" logs/gateway.log`
- `less logs/gateway.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
