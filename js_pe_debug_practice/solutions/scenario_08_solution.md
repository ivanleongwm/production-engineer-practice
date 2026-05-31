# Scenario 08 Solution - Firewall / Port Blocked

## Short answer / root cause

DNS resolves `risk.internal` correctly to `10.0.2.20`, but a **firewall rule blocks gateway (`10.0.1.50`) → risk port 9001**. Risk is healthy and reachable from engine, making this a **source-specific connectivity** failure, not a risk outage.

## Commands to run

```bash
grep -Rni "O8008" logs/
grep -Rni "connect_failed\|tcp_timeout\|port=9001" logs/gateway.log
grep -Rni "risk_ping\|heartbeat" logs/risk.log logs/engine.log
grep -Rni "firewall\|iptables\|DROP\|deny_gateway" logs/system.log
less logs/gateway.log
```

## Important log lines to notice

- `system.log`: `dig_lookup hostname=risk.internal resolved_ip=10.0.2.20 status=ok` — DNS works
- `gateway.log`: `connect_failed remote_host=10.0.2.20 port=9001 reason=tcp_timeout waited_ms=4000`
- `risk.log`: heartbeat `listen_ip=10.0.2.20 port=9001 status=healthy`
- `engine.log`: `risk_ping ... status=connected latency_ms=3` — another service reaches risk
- `system.log`: `iptables drop_logged src=10.0.1.50 dst=10.0.2.20 dport=9001 rule=deny_gateway_to_risk_9001`

## Red herrings to ignore

- `tcp_timeout` can look like risk is down — compare with engine’s successful ping
- Unrelated risk latency warnings on other orders
- DNS failure symptoms would show bad/missing `resolved_ip`, not successful dig

## First divergence

At **gateway TCP connect to risk:9001** — timeout after 4s while DNS succeeded and risk process is listening.

## Immediate mitigation

- Open firewall rule allowing gateway subnet → risk:9001
- Fail over gateway to a host with correct egress rules (if alternate path exists)
- Drain/reject new orders at gateway with clear alert while rule is fixed

## Long-term fix

- Infrastructure-as-code for firewall rules tied to service deploys
- Synthetic connectivity checks from gateway → each downstream port (not just health endpoints)
- Distinguish timeout (filtered/blackholed) vs refused (nothing listening) in alerts

## 60-second interview explanation

"Order O8008 failed with RISK_UNREACHABLE, but risk heartbeats are fine and engine reaches risk on port 9001. DNS dig from gateway succeeds. Gateway logs show TCP timeout to `10.0.2.20:9001`, and system.log has an iptables DROP from gateway IP to that port. First divergence is network policy, not DNS or risk health. I'd open the firewall path immediately and add gateway-origin connectivity probes so this is caught before orders fail."
