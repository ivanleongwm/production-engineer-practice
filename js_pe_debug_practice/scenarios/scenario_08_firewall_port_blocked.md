# Scenario 08 - Firewall / Port Blocked

## Incident report

Order `O8008` (MSFT, 200 shares, client `C808`) was rejected with `RISK_UNREACHABLE`. Risk team says their service is healthy. Engine team says they can reach risk fine.

## Goal

Determine why gateway cannot reach risk while other paths succeed.

## Suggested commands to try (no answer)

- `grep -Rni "O8008" logs/`
- `grep -Rni "connect_failed\|tcp_timeout\|port=9001" logs/`
- `grep -Rni "firewall\|iptables\|DROP" logs/system.log`
- `less logs/gateway.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
