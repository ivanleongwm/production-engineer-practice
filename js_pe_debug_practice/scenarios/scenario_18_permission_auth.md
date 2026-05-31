# Scenario 18 - Permission / Auth Issue

## Incident report

Only client `C1818` cannot submit orders on `0700.HK`. Order `O1818` was rejected. Other clients trading the same symbol are unaffected.

## Goal

Determine whether this is a system-wide outage or a client-specific entitlement problem.

## Suggested commands to try (no answer)

- `grep -Rni "O1818\|C1818" logs/`
- `grep -Rni "permission_denied\|entitlement\|AUTH" logs/`
- `grep -Rni "0700.HK" logs/gateway.log`
- `less logs/gateway.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
