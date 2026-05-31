# Scenario 10 - Bad Deploy / Config Mismatch

## Incident report

After a morning deployment, client `C1010` reports unexpected risk rejects on `9988.HK`. Order `O1010` (500 shares) was rejected. AAPL orders from the same client still pass.

## Goal

Correlate the reject with a recent change and identify blast radius.

## Suggested commands to try (no answer)

- `grep -Rni "O1010\|9988.HK" logs/`
- `grep -Rni "config_deployed\|config_version\|deploy" logs/system.log`
- `grep -Rni "max_qty\|bucket\|RISK_LIMIT" logs/risk.log`
- `less logs/risk.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
