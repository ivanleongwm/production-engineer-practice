# Interviewer Guide — Meridian Order Platform Mock PE Interview

**Audience:** Interviewer only. Do not share with candidates during Part 1.

**Duration:** 60–75 minutes  
**Format:** System comprehension → design discussion → live debugging (one of three bugs)

---

## Running the interview

### Before the session

```bash
cd js_pe_mock_interview
python scripts/reset_logs.py
python scripts/run_normal.py   # optional: verify repo works
```

Give candidate access to repo root, `README.md`, code, config, and logs. **Hide this file** until wrap-up or if they finish early.

### Part 1 prompt (read aloud)

> "This is an unfamiliar order-processing system. Spend about 15 minutes exploring the repo — README, config, code, and a normal run. Then walk me through the architecture: components, happy path, state, config, rejection points, and what you'd improve. I'll ask follow-ups."

Run: `python scripts/run_normal.py` (candidate or you)

### Part 2 prompt (pick ONE bug)

Reset logs before each incident: `python scripts/reset_logs.py`

| Bug | Command | Verbal prompt |
|-----|---------|---------------|
| A | `python scripts/run_bug_a.py` | "C17 says BABA orders fail with ROUTE_NOT_FOUND. JD and AAPL work. Debug ORD-A03." |
| B | `python scripts/run_bug_b.py` | "C21 says LIMIT_EXCEEDED on ORD-B03 even though notional equals their limit. Other C21 orders work." |
| C | `python scripts/run_bug_c.py` | "Retry of ORD-C01: client got REJECTED but ops says order_service DB still shows ACKED. Trace the duplicate." |

---

## Expected architecture explanation

### Components

| Component | Role |
|-----------|------|
| `client_simulator` | Submits orders; receives final response |
| `gateway` | Ingress validation: qty/price, symbol enabled, client known, entitlements |
| `order_service` | In-memory order DB + audit trail |
| `risk_engine` | Notional limit check per client |
| `order_router` | Maps symbol → venue via `config/routes*.json` |
| `matching_engine` | Executes order; rejects duplicate `order_id` |
| `execution_publisher` | Publishes fill to downstream topic |
| `position_service` | Updates positions from fills |
| `pipeline.py` | Wires in-process calls in sequence |
| `system.log` | Health-check noise |

### Normal order flow

```
client_simulator.submit
  → gateway.receive (RECEIVED → VALIDATED or REJECTED)
  → order_service.register
  → risk_engine.evaluate (RISK_ACCEPTED or RISK_REJECTED)
  → order_router.route (ROUTED or ROUTE_NOT_FOUND)
  → matching_engine.submit (FILLED or DUPLICATE_ORDER_ID)
  → execution_publisher.publish (PUBLISHED)
  → position_service.apply_fill
  → gateway.ack_to_client (ACKED)
  → client_simulator.receive_response
```

### State stored

| Location | State |
|----------|-------|
| `order_service._records` | Per-order lifecycle state (in-memory DB) |
| `order_service` audit log | Append-only state transitions |
| `matching_engine._seen_order_ids` | Dedup set for order_id |
| `matching_engine._fills` | exec_id per order |
| `execution_publisher._published` | Published exec_ids |
| `position_service._positions` | (client_id, symbol) → qty |
| Config files | Symbols, client limits, routes (read-only at runtime) |

### Config files

- `config/symbols.json` — symbol enabled/disabled, tick/lot metadata
- `config/clients.json` — `notional_limit`, `allowed_symbols`
- `config/routes.json` — symbol → venue (`US_EQUITY`, `HK_EQUITY`, `CN_EQUITY`)

### Rejection points

| Stage | Reasons |
|-------|---------|
| Gateway | `BAD_QTY`, `BAD_PRICE`, `SYMBOL_DISABLED`, `UNKNOWN_CLIENT`, `SYMBOL_NOT_ALLOWED` |
| Risk | `LIMIT_EXCEEDED` |
| Router | `ROUTE_NOT_FOUND` |
| Matching engine | `DUPLICATE_ORDER_ID` |

### Expected comprehension answers (strong)

- Logs are **per-component**; must correlate by `order_id` / `request_id`
- `order_service` is the **system of record** for order state — but may diverge from downstream if updated incorrectly
- Duplicate handling belongs in **matching_engine** (and ideally idempotent ingress)
- Partial failure: if matching fails after risk accept, client should not get ACK; state should reflect REJECTED or PENDING — not ACKED
- Retries with same `order_id` should be **idempotent** or use new client order id with dedup key

### Design issues candidates may raise (good signals)

- No explicit `PENDING` / `SENT_TO_ENGINE` state before final ACK
- `order_service` updates state synchronously without two-phase confirm
- No distributed tracing — only log correlation IDs
- Config loaded at startup; no hot reload visibility in logs
- In-process simulation hides network timeout / partial failure classes
- No metrics — only logs and heartbeats

---

## Bug A — Missing route for BABA

### Symptom

- Orders for symbol `BABA` from client `C17` fail with `ROUTE_NOT_FOUND`
- `JD`, `AAPL` succeed for same client

### Root cause

`scripts/run_bug_a.py` loads `config/routes_bug_a.json` which **omits the `BABA` entry** (present in normal `routes.json`). Validation and risk pass; failure first appears at `order_router`.

### Key log lines

```
order_router.log: route_missing ... order_id=ORD-A03 symbol=BABA reason=ROUTE_NOT_FOUND config_key=BABA available_routes=...
order_router.log: (compare) route_selected ... order_id=ORD-A02 symbol=JD state=ROUTED route=HK_EQUITY
risk_engine.log: risk_accept ... order_id=ORD-A03
gateway.log: forward_to_order_service ... order_id=ORD-A03 state=VALIDATED
```

### Expected candidate commands

```bash
grep -Rni "ORD-A03" logs/
grep -Rni "ROUTE_NOT_FOUND" logs/
grep -Rni "BABA" logs/order_router.log logs/risk_engine.log
diff config/routes.json config/routes_bug_a.json   # if they find routes_bug_a.json
cat config/routes.json
grep -Rni "ORD-A02" logs/order_router.log   # working JD comparison
```

### Expected reasoning

1. Trace ORD-A03 through gateway → order_service → risk (all pass)
2. First failure at order_router with `ROUTE_NOT_FOUND`
3. Compare BABA vs JD: JD has route, BABA missing from routes config
4. Not risk, not gateway entitlement — **config gap**

### Hints if stuck

- L1: "Which component emits ROUTE_NOT_FOUND?"
- L2: "Compare order_router logs for ORD-A02 vs ORD-A03"
- L3: "What config file does order_router read?"

### Strong signals

- Names `config/routes.json` (or discovers `routes_bug_a.json` used by script)
- Identifies **first divergence** at router, not client
- Mentions blast radius: all BABA orders, not all clients

### Weak signals

- Blames risk or client entitlement without log evidence
- Stops at "ROUTE_NOT_FOUND" without config root cause
- Only reads client_simulator logs

---

## Bug B — Inclusive limit boundary (`>=` vs `>`)

### Symptom

- Client `C21` receives `LIMIT_EXCEEDED` on ORD-B03: qty=100, price=1000 → notional=100,000
- `config/clients.json` shows C21 `notional_limit`: 100000
- ORD-B01, ORD-B04 succeed (under limit)

### Root cause

`scripts/run_bug_b.py` sets `inclusive_limit_bug=True` on `RiskEngine`, which rejects when `notional >= limit` instead of correct `notional > limit`. Order at **exactly** the limit fails.

### Key log lines

```
risk_engine.log: risk_eval_start ... order_id=ORD-B03 notional=100000.0 client_limit=100000.0
risk_engine.log: risk_reject ... reason=LIMIT_EXCEEDED check="notional >= limit"
risk_engine.log: (compare ORD-B01) risk_accept ... notional=20000.0 check="notional >= limit"
```

Candidate should read `trading_system/risk_engine.py` and spot comparator.

### Expected candidate commands

```bash
grep -Rni "ORD-B03" logs/
grep -Rni "LIMIT_EXCEEDED" logs/risk_engine.log
grep -Rni "C21" config/clients.json
python -c "print(100*1000)"   # or mental math
grep -Rni "inclusive\|>=" trading_system/risk_engine.py
```

### Expected reasoning

1. Compute notional = qty × price = 100,000
2. Compare to C21 limit = 100,000 — should pass if limit is exclusive upper bound
3. Risk log shows reject with `>=` check
4. Ask: **inclusive or exclusive limit?** — product decision, but code uses wrong operator

### Hints if stuck

- L1: "What is the notional for ORD-B03?"
- L2: "Read risk_engine.log check= field"
- L3: "Open risk_engine.py — how is breach computed?"

### Strong signals

- Calculates notional explicitly
- Questions inclusive vs exclusive semantics
- Proposes unit test at boundary (limit, limit−ε, limit+ε)

### Weak signals

- Assumes client misconfigured without checking math
- Suggests raising limit without identifying code bug

---

## Bug C — Early ACCEPT before matching_engine confirm

### Symptom

- Retry of `ORD-C01` (same `order_id`, new `request_id`) → client gets `DUPLICATE_ORDER_ID` reject
- `order_service` audit still shows `state=ACKED` for the retry path; DB not updated to REJECTED on duplicate

### Root cause

`scripts/run_bug_c.py` sets `early_accept_bug=True`. `order_service.mark_early_accepted()` writes `ACKED` to DB **before** matching_engine runs. On duplicate, matching_engine rejects, but bug path **does not overwrite** ACKED → state inconsistency.

### Key log lines

```
order_service.log: audit_update ... order_id=ORD-C01 request_id=REQ-C01-RETRY state=ACKED note=early_accept_before_matching_engine
matching_engine.log: duplicate_order ... order_id=ORD-C01 reason=DUPLICATE_ORDER_ID
order_service.log: state_inconsistency db_state=ACKED downstream_state=REJECTED reason=DUPLICATE_ORDER_ID
gateway.log: ack_to_client ... state=REJECTED reason=DUPLICATE_ORDER_ID
client_simulator.log: order_response ... state=REJECTED reason=DUPLICATE_ORDER_ID
```

First ORD-C01 succeeds (FILLED/PUBLISHED). Retry is the problematic one.

### Expected candidate commands

```bash
grep -Rni "ORD-C01" logs/
grep -Rni "DUPLICATE_ORDER_ID" logs/
grep -Rni "early_accept\|state_inconsistency" logs/order_service.log
grep -Rni "mark_early_accepted" trading_system/
less trading_system/pipeline.py
```

### Expected reasoning

1. Trace both ORD-C01 submissions (note different request_id on retry)
2. First succeeds end-to-end
3. Retry: order_service logs ACKED **before** matching_engine duplicate reject
4. Client sees REJECTED; DB still ACKED — **premature state commit**
5. Propose `PENDING` / `SENT_TO_ENGINE` state; only ACK after matching confirms

### Hints if stuck

- L1: "Compare order_service vs matching_engine timestamps for the retry"
- L2: "When does order_service write ACKED?"
- L3: "Search for early_accept in pipeline.py"

### Strong signals

- Identifies **ordering bug** not duplicate bug per se
- Proposes two-phase commit / state machine fix
- Discusses safe retries (new idempotency key vs same order_id)

### Weak signals

- Says "duplicate orders are bad" without state machine analysis
- Only fixes matching_engine without order_service ordering

---

## Follow-up questions (any bug)

Use 2–3 at wrap-up:

| Question | Strong answer themes |
|----------|---------------------|
| How improve observability? | Structured correlation IDs everywhere; single trace view; state transition metrics; config version in logs |
| Safe retries? | Idempotency keys; dedup at gateway; PENDING state; client retry only on timeout with same client_order_id mapping |
| Metrics to add? | Reject rate by reason/layer; end-to-end latency histogram; route miss counter; risk boundary hits; duplicate rate |
| matching_engine slow? | Queue depth; backpressure at router; don't ACK early; timeout with cancel/reconcile |
| Alive vs healthy? | Process up ≠ config valid ≠ can reach downstream; readiness probes per dependency |
| First divergence? | Earliest log where expected ≠ actual for traced order_id |
| Narrow blast radius? | Symbol-scoped config; canary deploy; feature flags; drain bad LB instance |

---

## Rubric snapshot

| | Weak | Strong |
|---|------|--------|
| Exploration | Random grep | Builds happy path first |
| Debugging | Single log file | Cross-service trace |
| Root cause | Symptom restated | Layer + config/code identified |
| Communication | Jumps to fix | States evidence, divergence, blast radius |
| Design | Silent | Proposes observability + state machine improvements |

---

## Answer key quick reference (interviewer)

| Bug | Root cause | Fix |
|-----|------------|-----|
| A | `BABA` missing from routes config | Add `"BABA": "HK_EQUITY"` to routes |
| B | `>=` instead of `>` for limit | Use `notional > limit` for reject |
| C | ACK persisted before matching confirm | Introduce PENDING; ACK only after fill/ explicit reject overwrites |

```bash
python scripts/run_normal.py   # 5/5 success
python scripts/run_bug_a.py    # BABA orders fail
python scripts/run_bug_b.py    # ORD-B03 fails at exact limit
python scripts/run_bug_c.py    # ORD-C01 retry: DB ACKED, client REJECTED
```
