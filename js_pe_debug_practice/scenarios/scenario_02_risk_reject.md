# Scenario 02 - Risk Reject

## Incident report

Trader says: "Order O2002 was rejected unexpectedly. I thought it should pass risk."

## Goal

Determine whether the rejection is valid, and identify the first component that changes order state from expected accepted flow.

## Suggested commands to try (no answer)

- `grep -Rni "O2002" logs/`
- `grep -Rni "REJECT\\|RISK_LIMIT\\|risk_eval" logs/`
- `less logs/risk.log`
- `less logs/gateway.log`
- `tail -n 50 logs/system.log`

## Your notes

- expected behavior:
- actual behavior:
- correlation key:
- system path:
- first divergence:
- hypothesis:
- verification:
- fix:
- prevention:
