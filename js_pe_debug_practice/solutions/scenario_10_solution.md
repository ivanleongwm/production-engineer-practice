# Scenario 10 Solution - Bad Deploy / Config Mismatch

## Short answer / root cause

A morning deploy of **`risk-config-v2.14.1`** mis-mapped symbol **`9988.HK`** to the wrong risk bucket (`HK_SMALL_CAP_MISMAP`) with **max_qty=100**, causing valid-looking rejects for qty=500. Other symbols (e.g. AAPL) still pass under the same config version.

## Commands to run

```bash
grep -Rni "O1010\|9988.HK\|O1011" logs/
grep -Rni "config_deployed\|config_version\|deploy" logs/system.log
grep -Rni "max_qty\|bucket\|RISK_LIMIT" logs/risk.log
grep -Rni "risk_eval" logs/risk.log | grep -i "9988\|AAPL"
less logs/risk.log
```

## Important log lines to notice

- `system.log`: `config_deployed target_service=risk version=risk-config-v2.14.1 changed_keys=symbol_bucket_map,max_qty_map`
- `risk.log`: `O1010 ... symbol=9988.HK qty=500 status=REJECT reason=max_qty_breach limit=100 bucket=HK_SMALL_CAP_MISMAP config_version=risk-config-v2.14.1`
- `risk.log`: `O1011 symbol=AAPL qty=100 status=ACCEPT` — same deploy, different symbol OK
- `client.log`: reject reason `RISK_LIMIT` — looks like normal risk unless you check symbol scope

## Red herrings to ignore

- Generic `symbol_map stale_entries=BRK.B` noise — unrelated symbol
- RISK_LIMIT reject code alone — need to compare config version and symbol blast radius
- Assuming all symbols broken — only 9988.HK affected

## First divergence

At **risk eval for 9988.HK** using new bucket/limit from deploy — config change, not gateway or engine failure.

## Immediate mitigation

- Roll back risk config to previous version or hotfix symbol mapping for 9988.HK
- Communicate blast radius: only 9988.HK (verify no other HK symbols mis-mapped)
- Pause trading on affected symbol until config verified

## Long-term fix

- Config diff review in CI; canary deploy with symbol-level validation
- Automated post-deploy checks: known test orders per symbol bucket
- Version tag on every risk_eval log line (already present — use it in dashboards)

## 60-second interview explanation

"9988.HK rejects started after deploy. I found config_deployed risk-config-v2.14.1 changing symbol_bucket_map. O1010 hits max_qty_breach limit=100 in bucket HK_SMALL_CAP_MISMAP; O1011 AAPL accepts on the same config version. First divergence is post-deploy risk config for one symbol, not infrastructure. I'd roll back or hotfix the mapping, confirm blast radius is symbol-scoped, and add canary validation before full config rollout."
