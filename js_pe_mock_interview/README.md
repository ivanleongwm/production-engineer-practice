# Meridian Order Platform — Mock PE Interview Case Study

You have been dropped into an **unfamiliar trading order-processing codebase** for a simulated Jane Street Production Engineer second-round interview (60–75 minutes).

This repo is a self-contained Python simulation of a small multi-service order stack. Components run **in-process** (no real networking), but the code and logs are structured as if they were separate services.

Your job is to:

1. **Understand the system** — components, data flow, state, config, rejection points, design tradeoffs
2. **Debug live incidents** — trace orders through logs, find the first divergence, explain root cause and fixes

> This README describes the interview setup. It does **not** reveal the bugs. An interviewer would use `INTERVIEWER_GUIDE.md` (not shown to candidates during Part 1).

---

## Setup

**Requirements:** Python 3.8+ (standard library only)

```bash
cd js_pe_mock_interview
python --version
python scripts/reset_logs.py
```

All commands below assume you are in the **repo root** (`js_pe_mock_interview/`).

---

## Repository layout

```
js_pe_mock_interview/
├── README.md                 # Candidate-facing (this file)
├── INTERVIEWER_GUIDE.md      # Interviewer-only answers & rubric
├── config/
│   ├── symbols.json          # Symbol metadata & enablement
│   ├── clients.json          # Client limits & entitlements
│   └── routes.json           # Symbol → venue routing
├── data/
│   ├── orders_normal.jsonl   # Happy-path sample orders
│   ├── orders_buggy.jsonl    # Mixed orders for exploration
│   └── orders_bug_*.jsonl    # Per-scenario order sets
├── logs/                     # Generated structured logs (gitignored content)
├── scripts/
│   ├── run_normal.py
│   ├── run_bug_a.py
│   ├── run_bug_b.py
│   ├── run_bug_c.py
│   └── reset_logs.py
└── trading_system/           # Simulated service modules
    ├── pipeline.py           # Orchestrator / wiring
    ├── client_simulator.py
    ├── gateway.py
    ├── order_service.py
    ├── risk_engine.py
    ├── order_router.py
    ├── matching_engine.py
    ├── execution_publisher.py
    └── position_service.py
```

---

## Running scenarios

### Normal flow (baseline)

```bash
python scripts/reset_logs.py
python scripts/run_normal.py
```

Expected: all orders in `data/orders_normal.jsonl` succeed. Inspect logs under `logs/`.

### Debugging scenarios (introduced by interviewer in Part 2)

The interviewer will ask you to investigate one of these. **Do not run all three before Part 2** if you are simulating a real interview.

```bash
python scripts/reset_logs.py
python scripts/run_bug_a.py   # Incident A

python scripts/reset_logs.py
python scripts/run_bug_b.py   # Incident B

python scripts/reset_logs.py
python scripts/run_bug_c.py   # Incident C
```

Each run overwrites `logs/*.log` with structured entries.

---

## Log format

Each service writes to its own file, e.g. `logs/gateway.log`, `logs/order_router.log`.

Fields are grep-friendly:

```
ts=... level=INFO component=gateway request_id=... order_id=... client_id=... symbol=... state=... message=...
```

Useful commands:

```bash
find logs -type f
wc -l logs/*
grep -Rni "ORD-A03" logs/
grep -Rni "ROUTE_NOT_FOUND\|LIMIT_EXCEEDED\|DUPLICATE" logs/
grep -Rni "level=ERROR\|level=WARN" logs/
less logs/order_router.log
```

See `trading_system/` source to understand which component emits which events.

---

## Order states

| State | Meaning |
|-------|---------|
| `RECEIVED` | Client submitted; gateway saw the order |
| `VALIDATED` | Passed ingress validation |
| `RISK_ACCEPTED` | Passed risk checks |
| `RISK_REJECTED` | Failed risk checks |
| `ROUTED` | Router selected a venue |
| `ACKED` | Client-facing success acknowledgement |
| `REJECTED` | Client-facing rejection |
| `FILLED` | Matching engine produced a fill |
| `PUBLISHED` | Execution report published |

## Reject reasons

`BAD_QTY`, `BAD_PRICE`, `SYMBOL_DISABLED`, `UNKNOWN_CLIENT`, `SYMBOL_NOT_ALLOWED`, `LIMIT_EXCEEDED`, `DUPLICATE_ORDER_ID`, `ROUTE_NOT_FOUND`

---

## Part 1 — System comprehension (≈15 min exploration + ≈20 min discussion)

**Exploration tasks** (read code, config, run normal flow):

1. What are the components and how do they call each other?
2. What is the **normal order flow** end-to-end?
3. What **state** is stored, and where?
4. Which **config files** control behavior?
5. Where can an order be **rejected**?
6. Which **logs** would you use to debug a stuck order?
7. What **design issues** do you notice (ordering, idempotency, observability)?
8. What should happen on **retries** and **duplicate order IDs**?
9. How should the system handle **partial failure**?

**Suggested exploration commands:**

```bash
python scripts/run_normal.py
grep -Rni "ORD-1004" logs/
cat config/routes.json
cat config/clients.json
less trading_system/pipeline.py
```

Do **not** read `INTERVIEWER_GUIDE.md` during Part 1.

---

## Part 2 — Live debugging (≈25 min)

The interviewer describes a symptom and runs one bug script. Your tasks:

1. Restate the **expected path** for the affected order
2. Find the **correlation key** (`order_id`, `request_id`)
3. Trace across `logs/*.log`
4. Identify the **first divergence**
5. Explain **root cause** and propose **mitigation + long-term fix**
6. Answer follow-ups (observability, retries, metrics, health vs alive)

Example interviewer prompt (Incident A):

> "Client C17 reports BABA orders fail. AAPL and JD work. Order ORD-A03 failed. Find why."

---

## Suggested timebox (60–75 min total)

| Phase | Time | Activity |
|-------|------|----------|
| Setup | 5 min | Orient to repo, run normal flow |
| System comprehension | 15 min | Read code/config/logs |
| Design discussion | 20 min | Tradeoffs, failure modes, improvements |
| Live debugging | 25 min | One bug scenario + follow-ups |
| Wrap-up | 5 min | Summary & candidate questions |

---

## Interview mindset

You are not expected to memorize this codebase. Strong candidates:

- Build a **mental model** of the happy path first
- **Correlate** by `order_id` / `request_id` across logs
- Separate **symptoms** (client reject) from **root cause layer** (config, boundary bug, state machine)
- Ask clarifying questions (inclusive vs exclusive limits, idempotency semantics)
- Propose **operational** fixes (rollback config, drain host) and **engineering** fixes (state machine, tests)

Good luck.
