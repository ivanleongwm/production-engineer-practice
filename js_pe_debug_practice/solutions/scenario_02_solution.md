# Scenario 02 Solution - Risk Reject

## Commands you should run

- `grep -Rni "O2002" logs/`
- `grep -Rni "decision=REJECT\\|RISK_LIMIT\\|max_notional_breach" logs/`
- `less logs/risk.log`
- `less logs/gateway.log`

## Log lines that matter

- `risk.log`: `decision=REJECT reason=max_notional_breach`
- `gateway.log`: rejection propagated to client with `code=RISK_LIMIT`
- `client.log`: rejection received

## First divergence

At risk evaluation: expected `ACCEPT`, actual `REJECT` because estimated notional exceeds configured limit.

## Likely root cause

Order size/notional violates risk limits. This is a business-rule rejection, not a platform outage.

## Interview explanation

"I correlated `order_id=O2002` end-to-end and found the first state change at risk. Gateway behavior is downstream-consistent, so the issue is valid policy enforcement. I would confirm whether the trader expected a limit override or stale limit configuration."
