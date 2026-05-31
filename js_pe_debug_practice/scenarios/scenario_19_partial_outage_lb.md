# Scenario 19 - Partial Outage / Bad LB Instance

## Incident report

Client `C1919` reports intermittent order failures on `O1919` (AAPL). Retrying sometimes works. No pattern by symbol — same client, same order type, mixed results.

## Goal

Identify whether one bad backend instance behind a load balancer is causing intermittent failures.

## Suggested commands to try (no answer)

- `grep -Rni "O1919\|O1920" logs/`
- `grep -Rni "loadbalancer\|backend_selected\|gateway-1\|gateway-2" logs/`
- `grep -Rni "stale_config\|CONFIG_ERROR" logs/gateway.log`
- `less logs/system.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
