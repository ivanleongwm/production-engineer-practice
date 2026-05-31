# Scenario 19 Solution - Partial Outage / Bad LB Instance

## Short answer / root cause

Load balancer routed **`O1919` to `gateway-2`**, which has **stale/invalid config** (`gateway-v1.9.0-stale`). **`gateway-1` is healthy**. Retry **`O1920`** hits gateway-1 and succeeds — classic **one bad backend behind LB**.

## Commands to run

```bash
grep -Rni "O1919\|O1920" logs/
grep -Rni "loadbalancer\|backend_selected\|gateway-1\|gateway-2" logs/
grep -Rni "stale_config\|CONFIG_ERROR\|degraded" logs/
less logs/system.log
less logs/gateway.log
```

## Important log lines to notice

- `system.log`: `backend_selected order_id=O1919 backend=gateway-2`
- `gateway.log` on gateway-host-2: `stale_config config_version=gateway-v1.9.0-stale reason=failed_validation`
- `gateway.log`: `reject_to_client reason=CONFIG_ERROR` for O1919
- `system.log`: `backend_health backend=gateway-1 status=healthy`; gateway-2 `status=degraded`
- `system.log`: `backend_selected order_id=O1920 backend=gateway-1` → order proceeds

## Red herrings to ignore

- Intermittent failure without checking *which backend*
- Assuming full gateway outage — gateway-1 fine
- Client-side retry success masking LB issue if you only look at one order

## First divergence

At **gateway-2 config validation failure** after LB routed O1919 to degraded instance.

## Immediate mitigation

- Drain/remove gateway-2 from LB pool
- Deploy fresh config to gateway-2 or restart with correct version
- Force sticky sessions off bad instance

## Long-term fix

- LB health checks tied to config version hash, not just TCP up
- Canary deploy per instance; auto-drain on config validation fail
- Log backend instance ID on every request for correlation

## 60-second interview explanation

"O1919 failed intermittently — LB sent it to gateway-2 which logged stale_config and CONFIG_ERROR. System.log shows gateway-2 degraded while gateway-1 healthy. Retry O1920 went to gateway-1 and worked. First divergence is one bad LB backend, not total gateway failure. I'd drain gateway-2, fix its config, and tighten health checks to include config version validation."
