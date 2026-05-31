# Scenario 09 Solution - Process Down / Not Listening

## Short answer / root cause

The **order_router process crashed (OOMKilled)** on `router-host-1`, so **nothing is listening on port 9100**. The host is reachable via ping, but connections get **ECONNREFUSED** — classic “host up, process down.”

## Commands to run

```bash
grep -Rni "O9009" logs/
grep -Rni "connection_refused\|ECONNREFUSED\|port=9100" logs/gateway.log
grep -Rni "OOMKilled\|process_exit\|restart_attempt" logs/system.log
grep -Rni "not_listening\|ss -lntp" logs/system.log
less logs/system.log
```

## Important log lines to notice

- `gateway.log`: `connect_failed remote_host=10.0.3.30 port=9100 reason=connection_refused errno=ECONNREFUSED`
- `system.log`: `process_exit reason=OOMKilled` on `order_router`
- `system.log`: `ss ... port_9100=not_listening`
- `system.log`: `host_reachable target_host=10.0.3.30 icmp=ok` — network fine
- `system.log`: supervisor `restart_attempt target_service=order_router`

## Red herrings to ignore

- Host ping success — does not imply the service port is open
- TCP timeout (scenario 08) vs refused here — refused means nothing listening
- Unrelated gateway worker restart warnings

## First divergence

At **order_router process exit (OOM)** before gateway’s connect attempt — port 9100 never bound.

## Immediate mitigation

- Restart order_router; verify port 9100 listening via `ss -lntp`
- Increase memory limit or reduce router heap if OOM recurs
- Route orders through backup router instance if available

## Long-term fix

- Memory limits, OOM alerts, and autoscaling for router
- Readiness probes that fail when port 9100 is not listening
- Post-restart validation in supervisor before marking instance healthy

## 60-second interview explanation

"O9009 failed with ROUTER_UNREACHABLE. Gateway gets ECONNREFUSED on port 9100, not timeout — that means the host answered but nothing listened. System.log shows order_router OOMKilled and ss confirms port 9100 not listening, while ping to the host succeeds. First divergence is process crash, not network. I'd restart the router, confirm the port is bound, and add OOM/memory alerting plus proper readiness checks."
