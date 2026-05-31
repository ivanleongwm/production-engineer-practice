# Scenario 09 - Process Down / Not Listening

## Incident report

Order `O9009` (GOOG, 75 shares) failed with `ROUTER_UNREACHABLE`. Network team confirms the router host responds to ping.

## Goal

Determine whether this is a network issue or a local process/listener problem.

## Suggested commands to try (no answer)

- `grep -Rni "O9009" logs/`
- `grep -Rni "connection_refused\|ECONNREFUSED\|port=9100" logs/`
- `grep -Rni "OOMKilled\|process_exit\|not_listening" logs/system.log`
- `less logs/system.log`

## Your notes

Use `scenarios/README_RCA_TEMPLATE.md` for your full write-up.
