# Scenario 18 Solution - Permission / Auth Issue

## Short answer / root cause

Client **`C1818` lacks entitlement `HK_EQUITY_PROD`** for symbol **`0700.HK`** in PROD. Gateway rejects at **auth layer** before risk. Client **`C707`** succeeds on same symbol — **one-user scope**, system otherwise healthy.

## Commands to run

```bash
grep -Rni "O1818\|C1818\|O1819" logs/
grep -Rni "permission_denied\|entitlement\|AUTH_PERMISSION" logs/
grep -Rni "0700.HK" logs/gateway.log
less logs/gateway.log
```

## Important log lines to notice

- `gateway.log`: `permission_denied client_id=C1818 symbol=0700.HK environment=PROD reason=missing_entitlement required=HK_EQUITY_PROD`
- `gateway.log`: `reject_to_client reason=AUTH_PERMISSION` — never reaches risk
- `gateway.log`: `permission_ok client_id=C707 ... entitlement=HK_EQUITY_PROD` for O1819
- No risk.log lines for O1818 — rejected at gateway auth

## Red herrings to ignore

- System-wide health checks all green
- Symbol mapping stale warnings for BRK.B — different issue
- Assuming HK market outage — other clients trade 0700.HK fine

## First divergence

At **gateway auth/permission check** for C1818 — before order routing to risk.

## Immediate mitigation

- Grant C1818 the HK_EQUITY_PROD entitlement (or correct environment mapping)
- Verify entitlement cache refreshed on gateway
- Confirm client is on intended environment (PROD vs UAT)

## Long-term fix

- Self-service entitlement audit tooling for ops
- Clear client-facing error: missing entitlement vs system failure
- Automated tests per client_id × symbol × environment matrix

## 60-second interview explanation

"Only C1818 can't trade 0700.HK. Gateway logs permission_denied missing_entitlement HK_EQUITY_PROD for O1818, rejected before risk. O1819 from C707 on same symbol gets permission_ok and routes normally. First divergence is client entitlement, not infrastructure. I'd grant the entitlement, refresh auth cache, and improve error messaging so traders know it's account scope not system down."
