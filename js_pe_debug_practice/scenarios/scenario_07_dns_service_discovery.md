# Scenario 07 - DNS / Service Discovery Issue

## Incident report

Client `C707` reports it cannot submit orders through the gateway hostname. Order `O7007` (AAPL, 100 shares) never reaches the gateway. Other desk clients appear unaffected.

## Goal

Determine whether this is a full gateway outage, a network partition, or a resolution problem.

## Suggested commands to try (no answer)

- `grep -Rni "O7007" logs/`
- `grep -Rni "gateway.internal\|resolved_ip\|dig\|nslookup" logs/`
- `grep -Rni "connect_failed\|connection_timeout" logs/client.log`
- `less logs/system.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
