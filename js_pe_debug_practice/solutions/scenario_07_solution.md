# Scenario 07 Solution - DNS / Service Discovery Issue

## Short answer / root cause

The client resolves `gateway.internal` to a **stale IP (`10.0.1.99`)** while the live gateway listens on **`10.0.1.50`**. Gateway is healthy; the client’s DNS cache/resolv config was not updated after the gateway IP change.

## Commands to run

```bash
grep -Rni "O7007" logs/
grep -Rni "gateway.internal\|resolved_ip\|dig\|nslookup" logs/system.log logs/client.log
grep -Rni "connect_failed\|connection_timeout\|10.0.1" logs/client.log
grep -Rni "listen_ip\|service_up\|heartbeat" logs/gateway.log logs/system.log
less logs/system.log
```

## Important log lines to notice

- `system.log`: authoritative `dig_lookup` → `resolved_ip=10.0.1.50` (correct)
- `system.log`: client-side `nslookup` → `resolved_ip=10.0.1.99`, `reason=stale_cache`
- `client.log`: `resolve_gateway` uses `10.0.1.99`; `connect_failed` with `connection_timeout`
- `gateway.log`: heartbeat on `listen_ip=10.0.1.50` — gateway is up on the correct address
- `system.log`: note `authoritative_correct_while_client_stale`

## Red herrings to ignore

- Generic `ntp_offset_ms` or timezone warnings — not the connectivity root cause
- Unrelated successful orders from other clients hitting the correct IP/path
- `connect_failed` alone does not mean gateway is down — check *which IP* was targeted

## First divergence

At **client DNS resolution**: client chooses `10.0.1.99` instead of authoritative `10.0.1.50` before any TCP attempt to the live gateway.

## Immediate mitigation

- Flush client DNS cache / restart resolver; point client at current service-discovery endpoint
- Temporarily configure client with correct gateway IP or updated `/etc/resolv.conf`
- Verify with `dig gateway.internal` from the affected client host

## Long-term fix

- Lower TTL on gateway DNS records; automate client-side cache invalidation on deploy
- Health checks should validate **hostname resolution path**, not just service heartbeat
- Alert on mismatch between authoritative DNS and client-resolved IP

## 60-second interview explanation

"The user cannot reach the gateway hostname, but gateway heartbeats show healthy on `10.0.1.50`. I grepped DNS evidence: authoritative dig returns the correct IP, while the client nslookup still has `10.0.1.99` with a stale TTL. The first divergence is client-side DNS resolution — the client connects to a dead/old IP and times out. This is not a gateway outage. I'd flush stale DNS on the client immediately and fix service-discovery propagation so all clients pick up the new IP after deploy."
