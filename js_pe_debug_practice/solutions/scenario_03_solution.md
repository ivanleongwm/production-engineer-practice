# Scenario 03 Solution - Gateway Timeout

## Commands you should run

- `grep -Rni "O3003" logs/`
- `grep -Rni "timeout\\|waited_ms\\|processing_ms\\|p95_latency" logs/`
- `less logs/gateway.log`
- `less logs/risk.log`
- `less logs/system.log`

## Log lines that matter

- `gateway.log`: `timeout_ms=150`, then `risk_timeout waited_ms=153`
- `risk.log`: request took `processing_ms=240`, later `decision=ACCEPT`
- `system.log`: `svc=risk p95_latency_ms=232 threshold_ms=150`

## First divergence

At gateway timeout threshold enforcement. Risk responds too slowly relative to gateway timeout budget.

## Likely root cause

Timeout mismatch and elevated risk service latency caused false-negative rejections at gateway.

## Interview explanation

"I compared timing fields between gateway and risk. Gateway gives up at ~150ms, but risk completes around ~240ms. The first divergence is timeout policy, not functional validation. I’d align SLO/timeouts or reduce risk latency to avoid unnecessary rejects."
