#!/usr/bin/env python3
"""Generate deterministic trading-system logs for Production Engineer debug practice."""

import argparse
import os
import random
from datetime import datetime, timedelta, timezone


LOG_FILES = [
    "client.log",
    "gateway.log",
    "risk.log",
    "engine.log",
    "execution_publisher.log",
    "position.log",
    "system.log",
]

DIFFICULTY_CONFIG = {
    "easy": {"min_lines": 100, "max_lines": 200},
    "medium": {"min_lines": 300, "max_lines": 500},
    "hard": {"min_lines": 600, "max_lines": 1000},
}

DIFFICULTY_SEED = {"easy": 1, "medium": 2, "hard": 3}

NOISE_SYMBOLS = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "META", "NVDA", "9988.HK", "0700.HK", "BRK.B"]
NOISE_CLIENTS = ["C101", "C202", "C303", "C404", "C505", "C606", "C707", "C818", "C900", "C111"]
MISLEADING_WARNINGS = [
    ("system.log", "WARN", {"service": "md-feed", "component": "connectivity", "reason": "transient_spike", "latency_ms": 45}),
    ("gateway.log", "WARN", {"component": "rate_limiter", "reason": "burst_detected", "client_id": "C900", "action": "throttle_skipped"}),
    ("risk.log", "WARN", {"component": "cache", "reason": "stale_limit_snapshot", "age_ms": 820, "action": "refresh_scheduled"}),
    ("engine.log", "WARN", {"component": "book", "symbol": "BRK.B", "reason": "wide_spread", "spread_bps": 42}),
    ("execution_publisher.log", "WARN", {"component": "kafka", "reason": "broker_election", "partition": 3, "lag_ms": 12}),
    ("position.log", "WARN", {"component": "reconcile", "reason": "intraday_drift", "delta_shares": 0, "status": "within_tolerance"}),
    ("system.log", "WARN", {"service": "gateway", "component": "worker", "reason": "slow_healthcheck", "latency_ms": 88}),
    ("client.log", "WARN", {"component": "retry", "reason": "transient_socket_reset", "action": "retry_ok"}),
    ("system.log", "ERROR", {"service": "md-feed", "component": "tick", "reason": "stale_quote", "symbol": "XYZ", "note": "non_order_path"}),
    ("gateway.log", "ERROR", {"component": "audit", "reason": "late_ack_metric", "order_id": "O9999", "note": "telemetry_only"}),
]

SCENARIO_META = {
    1: {"title": "Happy Path Baseline", "category": "baseline", "affected": {"order_id": "O1001", "client_id": "C101", "symbol": "AAPL"}},
    2: {"title": "Risk Reject", "category": "risk limit breach", "affected": {"order_id": "O2002", "client_id": "C202", "symbol": "TSLA"}},
    3: {"title": "Gateway Timeout", "category": "downstream timeout", "affected": {"order_id": "O3003", "client_id": "C303", "symbol": "NVDA"}},
    4: {"title": "Missing Execution Report", "category": "publish failure", "affected": {"order_id": "O4004", "client_id": "C404", "symbol": "MSFT"}},
    5: {"title": "Duplicate Fill / Wrong Position", "category": "duplicate processing", "affected": {"order_id": "O5005", "client_id": "C505", "symbol": "AMZN", "exec_id": "E5505"}},
    6: {"title": "Slow Order Latency", "category": "queue backlog", "affected": {"order_id": "O6006", "client_id": "C606", "symbol": "META"}},
    7: {"title": "DNS / Service Discovery Issue", "category": "stale DNS resolution", "affected": {"order_id": "O7007", "client_id": "C707", "symbol": "AAPL", "hostname": "gateway.internal", "stale_ip": "10.0.1.99", "correct_ip": "10.0.1.50"}},
    8: {"title": "Firewall / Port Blocked", "category": "port connectivity blocked", "affected": {"order_id": "O8008", "client_id": "C808", "symbol": "MSFT", "port": "9001", "blocked_path": "gateway->risk"}},
    9: {"title": "Process Down / Not Listening", "category": "process crash", "affected": {"order_id": "O9009", "client_id": "C909", "symbol": "GOOG", "port": "9100", "service": "order_router"}},
    10: {"title": "Bad Deploy / Config Mismatch", "category": "config mismatch post-deploy", "affected": {"order_id": "O1010", "client_id": "C1010", "symbol": "9988.HK", "deploy_version": "risk-config-v2.14.1"}},
    11: {"title": "Queue Consumer Lag", "category": "consumer lag", "affected": {"order_id": "O1111", "client_id": "C1111", "symbol": "NVDA", "exec_id": "E71111"}},
    12: {"title": "Duplicate Message / Idempotency", "category": "missing idempotency", "affected": {"order_id": "O1212", "client_id": "C1212", "symbol": "AMZN", "exec_id": "E71212"}},
    13: {"title": "Latency Spike / GC Pressure", "category": "GC pause / memory pressure", "affected": {"order_id": "O1313", "client_id": "C1313", "symbol": "META"}},
    14: {"title": "DB Connection Pool Exhaustion", "category": "connection pool exhausted", "affected": {"order_id": "O1414", "client_id": "C1414", "symbol": "TSLA"}},
    15: {"title": "Exchange Session Disconnect", "category": "FIX session disconnect", "affected": {"order_id": "O1515", "client_id": "C1515", "symbol": "AAPL", "session": "FIX-PROD-01"}},
    16: {"title": "Clock Skew / Misleading Timestamps", "category": "NTP clock skew", "affected": {"order_id": "O1616", "client_id": "C1616", "symbol": "MSFT", "skew_host": "engine-host-2"}},
    17: {"title": "Disk Full / Persistence Failure", "category": "disk full", "affected": {"order_id": "O1717", "client_id": "C1717", "symbol": "NVDA", "exec_id": "E71717", "host": "exec-pub-host-1"}},
    18: {"title": "Permission / Auth Issue", "category": "client entitlement missing", "affected": {"order_id": "O1818", "client_id": "C1818", "symbol": "0700.HK", "environment": "PROD"}},
    19: {"title": "Partial Outage / Bad LB Instance", "category": "load balancer bad instance", "affected": {"order_id": "O1919", "client_id": "C1919", "symbol": "AAPL", "bad_instance": "gateway-2"}},
    20: {"title": "Dependency Timeout / Vendor API Slow", "category": "external vendor latency", "affected": {"order_id": "O2020", "client_id": "C2020", "symbol": "BRK.B", "vendor": "refdata-vendor-api"}},
}


def timestamp_str(base, ms):
    value = base + timedelta(milliseconds=ms)
    return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(value.microsecond / 1000):03d}Z"


def format_log_line(base, ms, level, **fields):
    parts = [f"ts={timestamp_str(base, ms)}", f"level={level}"]
    for key, value in fields.items():
        parts.append(f"{key}={value}")
    return " ".join(parts)


class LogContext:
    """Builds deterministic logs for a scenario at a given difficulty."""

    def __init__(self, scenario_number, difficulty="medium"):
        self.scenario = scenario_number
        self.difficulty = difficulty
        seed = scenario_number * 10000 + DIFFICULTY_SEED[difficulty]
        self.rng = random.Random(seed)
        self.base = datetime(2026, 5, 28, 10, 0, 0, tzinfo=timezone.utc) + timedelta(minutes=scenario_number)
        self.logs = {name: [] for name in LOG_FILES}
        self.cursor_ms = 0

    def bump(self, minimum=40, maximum=180):
        self.cursor_ms += self.rng.randint(minimum, maximum)
        return self.cursor_ms

    def at(self, ms):
        self.cursor_ms = ms
        return ms

    def write(self, file_name, level, ms=None, **fields):
        if ms is None:
            ms = self.cursor_ms
        self.logs[file_name].append(format_log_line(self.base, ms, level, **fields))

    def total_lines(self):
        return sum(len(lines) for lines in self.logs.values())


def generate_health_checks(ctx, count):
    hosts = ["node-a", "node-b", "node-c", "gateway-host-1", "gateway-host-2", "risk-host-1", "engine-host-1", "engine-host-2", "exec-pub-host-1"]
    services = ["gateway", "risk", "engine", "execution_publisher", "position", "order_router"]
    for _ in range(count):
        ms = ctx.bump(800, 2500)
        host = ctx.rng.choice(hosts)
        service = ctx.rng.choice(services)
        cpu = ctx.rng.randint(18, 72)
        mem = ctx.rng.randint(35, 88)
        disk = ctx.rng.randint(41, 78)
        ctx.write(
            "system.log",
            "INFO",
            ms=ms,
            service="health-agent",
            host=host,
            component="healthcheck",
            event="periodic_check",
            cpu_pct=cpu,
            mem_pct=mem,
            disk_pct=disk,
            status="ok" if cpu < 85 else "degraded",
        )
        if ctx.rng.random() < 0.35:
            ctx.write(
                f"{service}.log" if service != "order_router" else "gateway.log",
                "INFO",
                ms=ms + ctx.rng.randint(5, 40),
                service=service,
                host=host,
                component="heartbeat",
                event="heartbeat",
                status="ok",
                pid=10000 + ctx.rng.randint(1, 999),
            )


def generate_misleading_warnings(ctx, count):
    for i in range(count):
        ms = ctx.bump(600, 2200)
        file_name, level, fields = MISLEADING_WARNINGS[i % len(MISLEADING_WARNINGS)]
        ctx.write(file_name, level, ms=ms, pid=12000 + i, host="node-a", **fields)


def generate_noise_order(ctx, index):
    ms_start = ctx.bump(500, 3000)
    order_id = f"O9{index:03d}"
    client_id = ctx.rng.choice(NOISE_CLIENTS)
    symbol = ctx.rng.choice(NOISE_SYMBOLS)
    qty = ctx.rng.choice([10, 25, 50, 100, 200])
    side = ctx.rng.choice(["BUY", "SELL"])
    price = round(ctx.rng.uniform(50, 500), 2)
    trace_id = f"T-{order_id}"
    pid = 13000 + index

    ctx.write("client.log", "INFO", ms=ms_start, service="client", host="client-host-1", pid=pid,
              component="order", event="order_send", order_id=order_id, client_order_id=f"CO-{order_id}",
              client_id=client_id, symbol=symbol, side=side, qty=qty, price=price, trace_id=trace_id)
    ctx.write("gateway.log", "INFO", ms=ms_start + 18, service="gateway", host=ctx.rng.choice(["gateway-host-1", "gateway-host-2"]),
              pid=14000 + index, component="ingress", event="order_received", order_id=order_id, client_id=client_id,
              symbol=symbol, side=side, qty=qty, trace_id=trace_id, latency_ms=ctx.rng.randint(3, 22))
    ctx.write("risk.log", "INFO", ms=ms_start + 55, service="risk", host="risk-host-1", pid=15000 + index,
              component="eval", event="risk_eval", order_id=order_id, client_id=client_id, symbol=symbol,
              side=side, qty=qty, status="ACCEPT", reason="within_limits", latency_ms=ctx.rng.randint(4, 18))
    ctx.write("gateway.log", "INFO", ms=ms_start + 95, service="gateway", host="gateway-host-1", pid=14000 + index,
              component="egress", event="ack_to_client", order_id=order_id, status="ACK", latency_ms=ctx.rng.randint(80, 140))
    if ctx.rng.random() < 0.7:
        exec_id = f"E9{index:04d}"
        ctx.write("engine.log", "INFO", ms=ms_start + 160, service="engine", host="engine-host-1", pid=16000 + index,
                  component="match", event="fill_generated", order_id=order_id, exec_id=exec_id, symbol=symbol,
                  side=side, qty=qty, price=price, trace_id=trace_id)
        ctx.write("execution_publisher.log", "INFO", ms=ms_start + 195, service="execution_publisher",
                  host="exec-pub-host-1", pid=17000 + index, component="publish", event="execution_published",
                  order_id=order_id, exec_id=exec_id, status="FILLED", latency_ms=ctx.rng.randint(2, 9))
        ctx.write("position.log", "INFO", ms=ms_start + 230, service="position", host="node-c", pid=18000 + index,
                  component="ledger", event="position_update", client_id=client_id, order_id=order_id,
                  exec_id=exec_id, symbol=symbol, delta=qty if side == "BUY" else -qty, trace_id=trace_id)


def common_order_start(ctx, order_id, client_id, symbol, qty, side="BUY", ms_base=900, client_order_id=None):
    trace_id = f"T-{order_id}"
    coid = client_order_id or f"CO-{order_id}"
    ctx.at(ms_base)
    ctx.write("client.log", "INFO", ms=ms_base, service="client", host="client-host-1", pid=9101,
              component="order", event="order_send", order_id=order_id, client_order_id=coid,
              client_id=client_id, symbol=symbol, side=side, qty=qty, trace_id=trace_id)
    ctx.write("gateway.log", "INFO", ms=ms_base + 20, service="gateway", host="gateway-host-1", pid=9201,
              component="ingress", event="order_received", order_id=order_id, client_id=client_id,
              symbol=symbol, side=side, qty=qty, trace_id=trace_id, latency_ms=6)
    ctx.write("gateway.log", "INFO", ms=ms_base + 40, service="gateway", host="gateway-host-1", pid=9201,
              component="router", event="order_routed", order_id=order_id, route="risk", svc="risk-v1", trace_id=trace_id)


def pad_logs_to_difficulty(ctx):
    cfg = DIFFICULTY_CONFIG[ctx.difficulty]
    target = ctx.rng.randint(cfg["min_lines"], cfg["max_lines"])
    noise_index = 100
    iteration = 0
    while ctx.total_lines() < target and iteration < 500:
        iteration += 1
        generate_health_checks(ctx, 1)
        if ctx.difficulty != "easy":
            generate_misleading_warnings(ctx, 1)
        if ctx.rng.random() < 0.55:
            generate_noise_order(ctx, noise_index)
            noise_index += 1
        if ctx.total_lines() >= target:
            break
    ctx.write("system.log", "WARN", ms=ctx.bump(500, 1500), service="telemetry", host="node-a",
              component="timezone", event="timezone_mismatch", reason="display_only",
              note="local_ts_may_differ_from_utc")


# ---------------------------------------------------------------------------
# Scenarios 1-6 (preserved behaviour, adapted to LogContext)
# ---------------------------------------------------------------------------

def scenario_1_happy_path(ctx):
    order_id, client_id, symbol, qty = "O1001", "C101", "AAPL", 100
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("risk.log", "INFO", ms=980, service="risk", host="risk-host-1", pid=9301, component="eval",
              event="risk_eval", order_id=order_id, client_id=client_id, symbol=symbol, qty=qty,
              status="ACCEPT", reason="within_limits")
    ctx.write("gateway.log", "INFO", ms=1015, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="ack_to_client", order_id=order_id, status="ACK", latency_ms=115)
    ctx.write("engine.log", "INFO", ms=1080, service="engine", host="engine-host-1", pid=9401,
              component="match", event="order_accepted", order_id=order_id, symbol=symbol, status="NEW")
    ctx.write("engine.log", "INFO", ms=1220, service="engine", host="engine-host-1", pid=9401,
              component="match", event="fill_generated", order_id=order_id, exec_id="E5001", qty=100, price=188.42)
    ctx.write("execution_publisher.log", "INFO", ms=1255, service="execution_publisher", host="exec-pub-host-1",
              pid=9501, component="publish", event="execution_published", order_id=order_id, exec_id="E5001",
              status="FILLED", latency_ms=5)
    ctx.write("position.log", "INFO", ms=1295, service="position", host="node-c", pid=9601,
              component="ledger", event="position_update", client_id=client_id, order_id=order_id,
              symbol=symbol, delta=100, new_position=220)
    ctx.write("client.log", "INFO", ms=1320, service="client", host="client-host-1", pid=9101,
              component="order", event="execution_received", order_id=order_id, exec_id="E5001", status="FILLED")


def scenario_2_risk_reject(ctx):
    order_id, client_id, symbol, qty = "O2002", "C202", "TSLA", 15000
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("risk.log", "WARN", ms=975, service="risk", host="risk-host-1", pid=9301, component="eval",
              event="risk_eval", order_id=order_id, client_id=client_id, symbol=symbol, qty=qty,
              status="REJECT", reason="max_notional_breach", limit=1000000, est_notional=2782500)
    ctx.write("gateway.log", "WARN", ms=1010, service="gateway", host="gateway-host-1", pid=9201,
              component="risk", event="order_rejected", order_id=order_id, source="risk", code="RISK_LIMIT")
    ctx.write("gateway.log", "INFO", ms=1030, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="reject_to_client", order_id=order_id, status="REJECTED", latency_ms=128)
    ctx.write("client.log", "WARN", ms=1060, service="client", host="client-host-1", pid=9101,
              component="order", event="order_reject_received", order_id=order_id, reason="RISK_LIMIT")


def scenario_3_gateway_timeout(ctx):
    order_id, client_id, symbol, qty = "O3003", "C303", "NVDA", 250
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("gateway.log", "INFO", ms=965, service="gateway", host="gateway-host-1", pid=9201,
              component="risk_client", event="call_risk", order_id=order_id, timeout_ms=150, downstream="risk-v1")
    ctx.write("risk.log", "INFO", ms=980, service="risk", host="risk-host-1", pid=9301,
              component="eval", event="request_received", order_id=order_id, latency_ms=240)
    ctx.write("gateway.log", "ERROR", ms=1118, service="gateway", host="gateway-host-1", pid=9201,
              component="risk_client", event="risk_timeout", order_id=order_id, waited_ms=153,
              reason="downstream_timeout", action="reject")
    ctx.write("gateway.log", "WARN", ms=1133, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="reject_to_client", order_id=order_id, status="REJECTED", reason="DOWNSTREAM_TIMEOUT")
    ctx.write("risk.log", "INFO", ms=1220, service="risk", host="risk-host-1", pid=9301,
              component="eval", event="risk_eval", order_id=order_id, status="ACCEPT", reason="within_limits")
    ctx.write("system.log", "WARN", ms=1080, service="risk", host="risk-host-1", pid=9301,
              component="metrics", event="latency_slo", p95_latency_ms=232, threshold_ms=150)


def scenario_4_missing_execution_report(ctx):
    order_id, client_id, symbol, qty = "O4004", "C404", "MSFT", 80
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("risk.log", "INFO", ms=980, service="risk", host="risk-host-1", pid=9301,
              component="eval", event="risk_eval", order_id=order_id, status="ACCEPT", reason="within_limits")
    ctx.write("gateway.log", "INFO", ms=1015, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="ack_to_client", order_id=order_id, status="ACK", latency_ms=108)
    ctx.write("engine.log", "INFO", ms=1180, service="engine", host="engine-host-1", pid=9401,
              component="match", event="fill_generated", order_id=order_id, exec_id="E5404", qty=80, price=421.11)
    ctx.write("execution_publisher.log", "ERROR", ms=1210, service="execution_publisher", host="exec-pub-host-1",
              pid=9501, component="publish", event="publish_failed", order_id=order_id, exec_id="E5404",
              reason="kafka_topic_not_found", topic="exec.reports.v2")
    ctx.write("execution_publisher.log", "WARN", ms=1250, service="execution_publisher", host="exec-pub-host-1",
              pid=9501, component="retry", event="retry_scheduled", order_id=order_id, exec_id="E5404", retry_in_ms=5000, attempt=1)
    ctx.write("client.log", "WARN", ms=1500, service="client", host="client-host-1", pid=9101,
              component="order", event="pending_execution", order_id=order_id, waited_ms=600)


def scenario_5_duplicate_fill_position_wrong(ctx):
    order_id, client_id, symbol, qty = "O5005", "C505", "AMZN", 40
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("risk.log", "INFO", ms=980, service="risk", host="risk-host-1", pid=9301,
              component="eval", event="risk_eval", order_id=order_id, status="ACCEPT", reason="within_limits")
    ctx.write("gateway.log", "INFO", ms=1015, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="ack_to_client", order_id=order_id, status="ACK", latency_ms=97)
    ctx.write("engine.log", "INFO", ms=1160, service="engine", host="engine-host-1", pid=9401,
              component="match", event="fill_generated", order_id=order_id, exec_id="E5505", qty=40, price=171.70)
    ctx.write("execution_publisher.log", "INFO", ms=1185, service="execution_publisher", host="exec-pub-host-1",
              pid=9501, component="publish", event="execution_published", order_id=order_id, exec_id="E5505", status="FILLED")
    ctx.write("position.log", "INFO", ms=1210, service="position", host="node-c", pid=9601,
              component="ledger", event="position_update", client_id=client_id, symbol=symbol,
              exec_id="E5505", delta=40, new_position=90)
    ctx.write("execution_publisher.log", "WARN", ms=1240, service="execution_publisher", host="exec-pub-host-1",
              pid=9501, component="retry", event="duplicate_publish", order_id=order_id, exec_id="E5505",
              reason="retry_without_idempotency_guard", attempt=2)
    ctx.write("position.log", "ERROR", ms=1265, service="position", host="node-c", pid=9601,
              component="ledger", event="position_update", client_id=client_id, symbol=symbol,
              exec_id="E5505", delta=40, new_position=130, reason="duplicate_exec_applied")


def scenario_6_slow_order_latency(ctx):
    order_id, client_id, symbol, qty = "O6006", "C606", "META", 120
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("gateway.log", "WARN", ms=955, service="gateway", host="gateway-host-1", pid=9201,
              component="queue", event="queue_enqueue", order_id=order_id, queue="gateway_to_risk", depth=1840)
    ctx.write("system.log", "WARN", ms=970, service="gateway", host="gateway-host-1", pid=9201,
              component="queue", event="backlog", queue="gateway_to_risk", depth=1840)
    ctx.write("system.log", "WARN", ms=975, service="gateway", host="gateway-host-1", pid=9201,
              component="worker", event="worker_state", worker="worker-3", state="down", restart_count=4)
    ctx.write("risk.log", "INFO", ms=1760, service="risk", host="risk-host-1", pid=9301,
              component="eval", event="risk_eval", order_id=order_id, status="ACCEPT", reason="within_limits", latency_ms=8)
    ctx.write("gateway.log", "INFO", ms=1820, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="ack_to_client", order_id=order_id, status="ACK", latency_ms=920)
    ctx.write("engine.log", "INFO", ms=1950, service="engine", host="engine-host-1", pid=9401,
              component="match", event="fill_generated", order_id=order_id, exec_id="E5606", qty=120, price=495.80)
    ctx.write("client.log", "WARN", ms=2030, service="client", host="client-host-1", pid=9101,
              component="order", event="slow_ack_observed", order_id=order_id, ack_latency_ms=920)


# ---------------------------------------------------------------------------
# Scenarios 7-20 (intermediate/hard)
# ---------------------------------------------------------------------------

def scenario_7_dns_issue(ctx):
    order_id, client_id, symbol, qty = "O7007", "C707", "AAPL", 100
    ctx.write("system.log", "INFO", ms=100, service="dns-monitor", host="node-a", pid=8001,
              component="dns", event="dig_lookup", hostname="gateway.internal", resolved_ip="10.0.1.50", ttl_s=30, source="authoritative")
    ctx.write("system.log", "INFO", ms=130, service="health-agent", host="gateway-host-1", pid=8002,
              component="healthcheck", event="service_up", target_service="gateway", target_host="gateway-host-1", listen_ip="10.0.1.50", port=8080, status="healthy")
    ctx.write("system.log", "WARN", ms=160, service="dns-monitor", host="client-host-1", pid=8003,
              component="dns", event="nslookup", hostname="gateway.internal", resolved_ip="10.0.1.99", ttl_s=86400,
              reason="stale_cache", note="client_resolv_conf_not_updated")
    ctx.write("client.log", "INFO", ms=880, service="client", host="client-host-1", pid=9101,
              component="connect", event="resolve_gateway", hostname="gateway.internal", resolved_ip="10.0.1.99", trace_id=f"T-{order_id}")
    ctx.write("client.log", "INFO", ms=900, service="client", host="client-host-1", pid=9101,
              component="order", event="order_send", order_id=order_id, client_order_id=f"CO-{order_id}",
              client_id=client_id, symbol=symbol, side="BUY", qty=qty, target_host="10.0.1.99", port=8080, trace_id=f"T-{order_id}")
    ctx.write("client.log", "ERROR", ms=3500, service="client", host="client-host-1", pid=9101,
              component="connect", event="connect_failed", order_id=order_id, target_host="10.0.1.99", port=8080,
              reason="connection_timeout", waited_ms=3000, trace_id=f"T-{order_id}")
    ctx.write("gateway.log", "INFO", ms=920, service="gateway", host="gateway-host-1", pid=9201,
              component="heartbeat", event="heartbeat", listen_ip="10.0.1.50", port=8080, status="ok")
    ctx.write("client.log", "ERROR", ms=3520, service="client", host="client-host-1", pid=9101,
              component="order", event="submit_failed", order_id=order_id, client_id=client_id, symbol=symbol,
              reason="cannot_reach_gateway", trace_id=f"T-{order_id}")
    ctx.write("system.log", "INFO", ms=3600, service="dns-monitor", host="node-a", pid=8001,
              component="dns", event="dig_lookup", hostname="gateway.internal", resolved_ip="10.0.1.50", ttl_s=30,
              note="authoritative_correct_while_client_stale")


def scenario_8_firewall_blocked(ctx):
    order_id, client_id, symbol, qty = "O8008", "C808", "MSFT", 200
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("system.log", "INFO", ms=850, service="dns-monitor", host="gateway-host-1", pid=8101,
              component="dns", event="dig_lookup", hostname="risk.internal", resolved_ip="10.0.2.20", status="ok")
    ctx.write("gateway.log", "INFO", ms=960, service="gateway", host="gateway-host-1", pid=9201,
              component="risk_client", event="connect_attempt", order_id=order_id, remote_host="10.0.2.20", port=9001, trace_id=f"T-{order_id}")
    ctx.write("gateway.log", "ERROR", ms=4960, service="gateway", host="gateway-host-1", pid=9201,
              component="risk_client", event="connect_failed", order_id=order_id, remote_host="10.0.2.20", port=9001,
              reason="tcp_timeout", waited_ms=4000, trace_id=f"T-{order_id}")
    ctx.write("risk.log", "INFO", ms=900, service="risk", host="risk-host-1", pid=9301,
              component="heartbeat", event="heartbeat", listen_ip="10.0.2.20", port=9001, status="healthy")
    ctx.write("engine.log", "INFO", ms=980, service="engine", host="engine-host-1", pid=9401,
              component="risk_client", event="risk_ping", remote_host="10.0.2.20", port=9001, status="connected", latency_ms=3,
              note="engine_reaches_risk_ok")
    ctx.write("system.log", "WARN", ms=5000, service="firewall-audit", host="node-b", pid=8102,
              component="iptables", event="drop_logged", src="10.0.1.50", dst="10.0.2.20", dport=9001,
              rule="deny_gateway_to_risk_9001", action="DROP")
    ctx.write("gateway.log", "WARN", ms=4980, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="reject_to_client", order_id=order_id, status="REJECTED", reason="RISK_UNREACHABLE")


def scenario_9_process_down(ctx):
    order_id, client_id, symbol, qty = "O9009", "C909", "GOOG", 75
    common_order_start(ctx, order_id, client_id, symbol, qty, ms_base=900)
    ctx.write("gateway.log", "INFO", ms=960, service="gateway", host="gateway-host-1", pid=9201,
              component="router_client", event="connect_attempt", order_id=order_id, remote_host="10.0.3.30", port=9100, trace_id=f"T-{order_id}")
    ctx.write("gateway.log", "ERROR", ms=962, service="gateway", host="gateway-host-1", pid=9201,
              component="router_client", event="connect_failed", order_id=order_id, remote_host="10.0.3.30", port=9100,
              reason="connection_refused", errno="ECONNREFUSED", trace_id=f"T-{order_id}")
    ctx.write("system.log", "ERROR", ms=800, service="order_router", host="router-host-1", pid=8201,
              component="process", event="process_exit", reason="OOMKilled", oom_score=987, restart_pending="true")
    ctx.write("system.log", "INFO", ms=820, service="supervisor", host="router-host-1", pid=8202,
              component="systemd", event="restart_attempt", target_service="order_router", status="starting")
    ctx.write("system.log", "INFO", ms=840, service="netstat-agent", host="router-host-1", pid=8203,
              component="ss", event="port_scan", cmd="ss -lntp", port_9100="not_listening", note="nothing_listening_on_9100")
    ctx.write("system.log", "INFO", ms=860, service="health-agent", host="router-host-1", pid=8204,
              component="ping", event="host_reachable", target_host="10.0.3.30", icmp="ok")
    ctx.write("gateway.log", "WARN", ms=980, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="reject_to_client", order_id=order_id, status="REJECTED", reason="ROUTER_UNREACHABLE")


def scenario_10_bad_deploy(ctx):
    order_id, client_id, symbol, qty = "O1010", "C1010", "9988.HK", 500
    ctx.write("system.log", "INFO", ms=200, service="deploy-agent", host="risk-host-1", pid=8301,
              component="deploy", event="config_deployed", target_service="risk", version="risk-config-v2.14.1",
              changed_keys="symbol_bucket_map,max_qty_map", deploy_user="ci-bot")
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("risk.log", "WARN", ms=990, service="risk", host="risk-host-1", pid=9301,
              component="eval", event="risk_eval", order_id=order_id, client_id=client_id, symbol=symbol, qty=qty,
              status="REJECT", reason="max_qty_breach", limit=100, config_version="risk-config-v2.14.1", bucket="HK_SMALL_CAP_MISMAP")
    ctx.write("gateway.log", "WARN", ms=1020, service="gateway", host="gateway-host-1", pid=9201,
              component="risk", event="order_rejected", order_id=order_id, source="risk", code="RISK_LIMIT")
    ctx.write("client.log", "WARN", ms=1050, service="client", host="client-host-1", pid=9101,
              component="order", event="order_reject_received", order_id=order_id, symbol=symbol, reason="RISK_LIMIT")
    # Other symbol passes fine
    ctx.write("client.log", "INFO", ms=1100, service="client", host="client-host-1", pid=9101,
              component="order", event="order_send", order_id="O1011", client_id="C1010", symbol="AAPL", side="BUY", qty=100)
    ctx.write("risk.log", "INFO", ms=1150, service="risk", host="risk-host-1", pid=9301,
              component="eval", event="risk_eval", order_id="O1011", symbol="AAPL", qty=100, status="ACCEPT", reason="within_limits",
              config_version="risk-config-v2.14.1")


def scenario_11_consumer_lag(ctx):
    order_id, client_id, symbol, qty, exec_id = "O1111", "C1111", "NVDA", 150, "E71111"
    trace_id = f"T-{order_id}"
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("risk.log", "INFO", ms=980, service="risk", host="risk-host-1", pid=9301,
              component="eval", event="risk_eval", order_id=order_id, status="ACCEPT", reason="within_limits", latency_ms=7)
    ctx.write("gateway.log", "INFO", ms=1010, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="ack_to_client", order_id=order_id, status="ACK", latency_ms=105, trace_id=trace_id)
    ctx.write("engine.log", "INFO", ms=1120, service="engine", host="engine-host-1", pid=9401,
              component="match", event="fill_generated", order_id=order_id, exec_id=exec_id, qty=qty, price=890.12, trace_id=trace_id)
    ctx.write("execution_publisher.log", "INFO", ms=1145, service="execution_publisher", host="exec-pub-host-1",
              pid=9501, component="publish", event="execution_published", order_id=order_id, exec_id=exec_id,
              status="FILLED", topic="exec.reports.v2", partition=2, offset=99122, latency_ms=4, trace_id=trace_id)
    ctx.write("system.log", "WARN", ms=1200, service="position", host="node-c", pid=9601,
              component="queue", event="consumer_lag", queue="exec.reports.v2", group="position-consumer",
              lag_messages=842, lag_ms=18500, partition=2)
    ctx.write("position.log", "WARN", ms=1180, service="position", host="node-c", pid=9601,
              component="consumer", event="poll_slow", queue="exec.reports.v2", batch_size=1, poll_latency_ms=420)
    ctx.write("client.log", "INFO", ms=1320, service="client", host="client-host-1", pid=9101,
              component="order", event="ack_received", order_id=order_id, status="ACK", trace_id=trace_id)
    ctx.write("position.log", "INFO", ms=19680, service="position", host="node-c", pid=9601,
              component="ledger", event="position_update", client_id=client_id, order_id=order_id, exec_id=exec_id,
              symbol=symbol, delta=qty, new_position=450, consume_lag_ms=18535, trace_id=trace_id)
    ctx.write("client.log", "WARN", ms=19700, service="client", host="client-host-1", pid=9101,
              component="order", event="late_fill_observed", order_id=order_id, exec_id=exec_id, waited_ms=18380, trace_id=trace_id)


def scenario_12_duplicate_idempotency(ctx):
    order_id, client_id, symbol, qty, exec_id = "O1212", "C1212", "AMZN", 60, "E71212"
    trace_id = f"T-{order_id}"
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("risk.log", "INFO", ms=980, service="risk", host="risk-host-1", pid=9301,
              component="eval", event="risk_eval", order_id=order_id, status="ACCEPT", reason="within_limits")
    ctx.write("gateway.log", "INFO", ms=1010, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="ack_to_client", order_id=order_id, status="ACK", latency_ms=98)
    ctx.write("engine.log", "INFO", ms=1150, service="engine", host="engine-host-1", pid=9401,
              component="match", event="fill_generated", order_id=order_id, exec_id=exec_id, qty=qty, price=178.55, trace_id=trace_id)
    ctx.write("execution_publisher.log", "INFO", ms=1175, service="execution_publisher", host="exec-pub-host-1",
              pid=9501, component="publish", event="execution_published", order_id=order_id, exec_id=exec_id,
              status="FILLED", attempt=1, trace_id=trace_id)
    ctx.write("position.log", "INFO", ms=1200, service="position", host="node-c", pid=9601,
              component="ledger", event="position_update", client_id=client_id, order_id=order_id, exec_id=exec_id,
              symbol=symbol, delta=qty, new_position=160, idempotency_key="none", trace_id=trace_id)
    ctx.write("execution_publisher.log", "WARN", ms=1225, service="execution_publisher", host="exec-pub-host-1",
              pid=9501, component="retry", event="publish_retry", order_id=order_id, exec_id=exec_id,
              reason="no_ack_from_broker", attempt=2, trace_id=trace_id)
    ctx.write("execution_publisher.log", "INFO", ms=1240, service="execution_publisher", host="exec-pub-host-1",
              pid=9501, component="publish", event="execution_published", order_id=order_id, exec_id=exec_id,
              status="FILLED", attempt=2, trace_id=trace_id)
    ctx.write("position.log", "ERROR", ms=1265, service="position", host="node-c", pid=9601,
              component="ledger", event="position_update", client_id=client_id, order_id=order_id, exec_id=exec_id,
              symbol=symbol, delta=qty, new_position=220, reason="duplicate_exec_applied", idempotency_key="none", trace_id=trace_id)


def scenario_13_gc_latency(ctx):
    order_id, client_id, symbol, qty = "O1313", "C1313", "META", 80
    trace_id = f"T-{order_id}"
    for i, rss in enumerate([512, 620, 780, 910, 1040]):
        ctx.write("system.log", "WARN", ms=200 + i * 400, service="gateway", host="gateway-host-1", pid=9201,
                  component="memory", event="rss_sample", rss_mb=rss, threshold_mb=900, gc_gen=2)
    common_order_start(ctx, order_id, client_id, symbol, qty, ms_base=2200)
    ctx.write("gateway.log", "WARN", ms=2180, service="gateway", host="gateway-host-1", pid=9201,
              component="gc", event="gc_pause", pause_ms=412, gc_type="major", rss_mb=1040)
    ctx.write("gateway.log", "INFO", ms=2600, service="gateway", host="gateway-host-1", pid=9201,
              component="risk_client", event="call_risk", order_id=order_id, latency_ms=398, trace_id=trace_id)
    ctx.write("risk.log", "INFO", ms=2610, service="risk", host="risk-host-1", pid=9301,
              component="eval", event="risk_eval", order_id=order_id, status="ACCEPT", reason="within_limits", latency_ms=6)
    ctx.write("gateway.log", "INFO", ms=2650, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="ack_to_client", order_id=order_id, status="ACK", latency_ms=455, trace_id=trace_id)
    ctx.write("client.log", "WARN", ms=2670, service="client", host="client-host-1", pid=9101,
              component="order", event="slow_ack_observed", order_id=order_id, ack_latency_ms=455, trace_id=trace_id)
    ctx.write("engine.log", "INFO", ms=2800, service="engine", host="engine-host-1", pid=9401,
              component="match", event="fill_generated", order_id=order_id, exec_id="E71313", qty=qty, price=502.10)


def scenario_14_db_pool_exhaustion(ctx):
    order_id, client_id, symbol, qty = "O1414", "C1414", "TSLA", 300
    trace_id = f"T-{order_id}"
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("system.log", "INFO", ms=850, service="postgres-monitor", host="db-host-1", pid=8401,
              component="db", event="healthcheck", status="healthy", connections=42, max_connections=200)
    ctx.write("risk.log", "WARN", ms=960, service="risk", host="risk-host-1", pid=9301,
              component="db_pool", event="pool_wait", order_id=order_id, pool_active=32, pool_max=32, pool_idle=0,
              waited_ms=0, trace_id=trace_id)
    ctx.write("risk.log", "ERROR", ms=3460, service="risk", host="risk-host-1", pid=9301,
              component="db_pool", event="pool_timeout", order_id=order_id, reason="connection_pool_exhausted",
              waited_ms=2500, pool_active=32, pool_max=32, pool_idle=0, trace_id=trace_id)
    ctx.write("gateway.log", "ERROR", ms=3480, service="gateway", host="gateway-host-1", pid=9201,
              component="risk_client", event="risk_timeout", order_id=order_id, waited_ms=2520, reason="downstream_timeout", trace_id=trace_id)
    ctx.write("gateway.log", "WARN", ms=3495, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="reject_to_client", order_id=order_id, status="REJECTED", reason="DOWNSTREAM_TIMEOUT", trace_id=trace_id)
    ctx.write("system.log", "WARN", ms=3500, service="risk", host="risk-host-1", pid=9301,
              component="db_pool", event="pool_metrics", pool_active=32, pool_max=32, pool_idle=0, waiting_threads=14)


def scenario_15_exchange_disconnect(ctx):
    order_id, client_id, symbol, qty = "O1515", "C1515", "AAPL", 100
    trace_id = f"T-{order_id}"
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("risk.log", "INFO", ms=980, service="risk", host="risk-host-1", pid=9301,
              component="eval", event="risk_eval", order_id=order_id, status="ACCEPT", reason="within_limits", trace_id=trace_id)
    ctx.write("gateway.log", "INFO", ms=1010, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="ack_to_client", order_id=order_id, status="ACK", latency_ms=102, trace_id=trace_id)
    ctx.write("engine.log", "INFO", ms=1080, service="engine", host="engine-host-1", pid=9401,
              component="router", event="order_accepted", order_id=order_id, symbol=symbol, status="NEW", trace_id=trace_id)
    ctx.write("gateway.log", "INFO", ms=1090, service="gateway", host="gateway-host-1", pid=9201,
              component="router", event="sent_to_exchange", order_id=order_id, session="FIX-PROD-01", trace_id=trace_id)
    ctx.write("system.log", "ERROR", ms=1100, service="order_router", host="router-host-1", pid=8501,
              component="fix", event="session_down", session="FIX-PROD-01", reason="sequence_mismatch",
              expected_seq=104882, received_seq=104880, action="disconnect")
    ctx.write("engine.log", "WARN", ms=1120, service="engine", host="engine-host-1", pid=9401,
              component="fix", event="exchange_ack_missing", order_id=order_id, session="FIX-PROD-01",
              waited_ms=500, trace_id=trace_id)
    ctx.write("client.log", "WARN", ms=1600, service="client", host="client-host-1", pid=9101,
              component="order", event="no_exchange_ack", order_id=order_id, internal_status="ACK", exchange_status="UNKNOWN", trace_id=trace_id)


def scenario_16_clock_skew(ctx):
    order_id, client_id, symbol, qty = "O1616", "C1616", "MSFT", 90
    seq = 1616001
    trace_id = f"T-{order_id}"
    ctx.write("system.log", "WARN", ms=150, service="ntp", host="engine-host-2", pid=8601,
              component="chrony", event="clock_offset", offset_s=4.8, source="time-sync-1", action="step_scheduled")
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("risk.log", "INFO", ms=980, service="risk", host="risk-host-1", pid=9301,
              component="eval", event="risk_eval", order_id=order_id, status="ACCEPT", reason="within_limits", seq=seq, trace_id=trace_id)
    ctx.write("gateway.log", "INFO", ms=1010, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="ack_to_client", order_id=order_id, status="ACK", seq=seq + 1, latency_ms=100, trace_id=trace_id)
    # Engine log shows earlier timestamp due to skew but seq proves order
    ctx.write("engine.log", "INFO", ms=950, service="engine", host="engine-host-2", pid=9402,
              component="ingress", event="order_received", order_id=order_id, symbol=symbol, seq=seq + 2,
              host_clock_skew_s=4.8, trace_id=trace_id, note="timestamp_appears_before_gateway_due_to_skew")
    ctx.write("engine.log", "INFO", ms=1180, service="engine", host="engine-host-2", pid=9402,
              component="match", event="fill_generated", order_id=order_id, exec_id="E71616", qty=qty, price=420.50, seq=seq + 3, trace_id=trace_id)
    ctx.write("execution_publisher.log", "INFO", ms=1210, service="execution_publisher", host="exec-pub-host-1",
              pid=9501, component="publish", event="execution_published", order_id=order_id, exec_id="E71616", seq=seq + 4, trace_id=trace_id)
    ctx.write("position.log", "INFO", ms=1240, service="position", host="node-c", pid=9601,
              component="ledger", event="position_update", client_id=client_id, order_id=order_id, exec_id="E71616", seq=seq + 5, trace_id=trace_id)


def scenario_17_disk_full(ctx):
    order_id, client_id, symbol, qty, exec_id = "O1717", "C1717", "NVDA", 120, "E71717"
    trace_id = f"T-{order_id}"
    common_order_start(ctx, order_id, client_id, symbol, qty)
    ctx.write("risk.log", "INFO", ms=980, service="risk", host="risk-host-1", pid=9301,
              component="eval", event="risk_eval", order_id=order_id, status="ACCEPT", reason="within_limits", trace_id=trace_id)
    ctx.write("gateway.log", "INFO", ms=1010, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="ack_to_client", order_id=order_id, status="ACK", latency_ms=99, trace_id=trace_id)
    ctx.write("engine.log", "INFO", ms=1140, service="engine", host="engine-host-1", pid=9401,
              component="match", event="fill_generated", order_id=order_id, exec_id=exec_id, qty=qty, price=885.00, trace_id=trace_id)
    ctx.write("system.log", "ERROR", ms=1150, service="execution_publisher", host="exec-pub-host-1", pid=9501,
              component="disk", event="disk_full", mount="/var/log/exec-publisher", usage_pct=100, avail_bytes=0)
    ctx.write("execution_publisher.log", "ERROR", ms=1165, service="execution_publisher", host="exec-pub-host-1",
              pid=9501, component="persist", event="write_failed", order_id=order_id, exec_id=exec_id,
              path="/var/log/exec-publisher/outbox/E71717.json", reason="no_space_left_on_device", trace_id=trace_id)
    ctx.write("execution_publisher.log", "WARN", ms=1180, service="execution_publisher", host="exec-pub-host-1",
              pid=9501, component="publish", event="publish_skipped", order_id=order_id, exec_id=exec_id,
              reason="outbox_write_failed", trace_id=trace_id)
    ctx.write("execution_publisher.log", "INFO", ms=1200, service="execution_publisher", host="exec-pub-host-1",
              pid=9501, component="heartbeat", event="heartbeat", status="up", note="process_alive_but_persist_failing")
    ctx.write("client.log", "WARN", ms=2000, service="client", host="client-host-1", pid=9101,
              component="order", event="pending_execution", order_id=order_id, waited_ms=900, trace_id=trace_id)


def scenario_18_permission_auth(ctx):
    order_id, client_id, symbol, qty = "O1818", "C1818", "0700.HK", 200
    trace_id = f"T-{order_id}"
    ctx.write("client.log", "INFO", ms=900, service="client", host="client-host-1", pid=9101,
              component="order", event="order_send", order_id=order_id, client_order_id=f"CO-{order_id}",
              client_id=client_id, symbol=symbol, side="BUY", qty=qty, trace_id=trace_id)
    ctx.write("gateway.log", "INFO", ms=920, service="gateway", host="gateway-host-1", pid=9201,
              component="ingress", event="order_received", order_id=order_id, client_id=client_id, symbol=symbol, trace_id=trace_id)
    ctx.write("gateway.log", "WARN", ms=940, service="gateway", host="gateway-host-1", pid=9201,
              component="auth", event="permission_denied", order_id=order_id, client_id=client_id, symbol=symbol,
              environment="PROD", reason="missing_entitlement", required="HK_EQUITY_PROD", trace_id=trace_id)
    ctx.write("gateway.log", "WARN", ms=960, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="reject_to_client", order_id=order_id, status="REJECTED", reason="AUTH_PERMISSION", trace_id=trace_id)
    ctx.write("client.log", "WARN", ms=980, service="client", host="client-host-1", pid=9101,
              component="order", event="order_reject_received", order_id=order_id, reason="AUTH_PERMISSION", trace_id=trace_id)
    # Other client succeeds
    ctx.write("client.log", "INFO", ms=1000, service="client", host="client-host-2", pid=9102,
              component="order", event="order_send", order_id="O1819", client_id="C707", symbol="0700.HK", side="BUY", qty=100, trace_id="T-O1819")
    ctx.write("gateway.log", "INFO", ms=1020, service="gateway", host="gateway-host-1", pid=9201,
              component="auth", event="permission_ok", order_id="O1819", client_id="C707", symbol="0700.HK", entitlement="HK_EQUITY_PROD")
    ctx.write("gateway.log", "INFO", ms=1040, service="gateway", host="gateway-host-1", pid=9201,
              component="router", event="order_routed", order_id="O1819", route="risk", trace_id="T-O1819")


def scenario_19_partial_outage_lb(ctx):
    order_id, client_id, symbol, qty = "O1919", "C1919", "AAPL", 100
    trace_id = f"T-{order_id}"
    ctx.write("system.log", "INFO", ms=100, service="loadbalancer", host="lb-host-1", pid=8701,
              component="routing", event="backend_selected", order_id=order_id, backend="gateway-2", algorithm="round_robin")
    ctx.write("client.log", "INFO", ms=900, service="client", host="client-host-1", pid=9101,
              component="order", event="order_send", order_id=order_id, client_order_id=f"CO-{order_id}",
              client_id=client_id, symbol=symbol, side="BUY", qty=qty, trace_id=trace_id)
    ctx.write("gateway.log", "ERROR", ms=920, service="gateway", host="gateway-host-2", pid=9202,
              component="config", event="stale_config", order_id=order_id, config_version="gateway-v1.9.0-stale",
              reason="failed_validation", trace_id=trace_id)
    ctx.write("gateway.log", "WARN", ms=940, service="gateway", host="gateway-host-2", pid=9202,
              component="egress", event="reject_to_client", order_id=order_id, status="REJECTED", reason="CONFIG_ERROR", trace_id=trace_id)
    ctx.write("system.log", "INFO", ms=960, service="loadbalancer", host="lb-host-1", pid=8701,
              component="health", event="backend_health", backend="gateway-1", status="healthy")
    ctx.write("system.log", "WARN", ms=970, service="loadbalancer", host="lb-host-1", pid=8701,
              component="health", event="backend_health", backend="gateway-2", status="degraded", reason="elevated_5xx")
    ctx.write("client.log", "WARN", ms=980, service="client", host="client-host-1", pid=9101,
              component="order", event="order_reject_received", order_id=order_id, reason="CONFIG_ERROR", trace_id=trace_id)
    # Retry hits good instance
    ctx.write("system.log", "INFO", ms=1100, service="loadbalancer", host="lb-host-1", pid=8701,
              component="routing", event="backend_selected", order_id="O1920", backend="gateway-1", algorithm="round_robin")
    ctx.write("client.log", "INFO", ms=1120, service="client", host="client-host-1", pid=9101,
              component="order", event="order_send", order_id="O1920", client_id=client_id, symbol=symbol, side="BUY", qty=qty, trace_id="T-O1920")
    ctx.write("gateway.log", "INFO", ms=1140, service="gateway", host="gateway-host-1", pid=9201,
              component="ingress", event="order_received", order_id="O1920", client_id=client_id, symbol=symbol, trace_id="T-O1920")
    ctx.write("gateway.log", "INFO", ms=1160, service="gateway", host="gateway-host-1", pid=9201,
              component="router", event="order_routed", order_id="O1920", route="risk", trace_id="T-O1920")


def scenario_20_vendor_timeout(ctx):
    order_id, client_id, symbol, qty = "O2020", "C2020", "BRK.B", 50
    trace_id = f"T-{order_id}"
    ctx.write("client.log", "INFO", ms=900, service="client", host="client-host-1", pid=9101,
              component="order", event="order_send", order_id=order_id, client_order_id=f"CO-{order_id}",
              client_id=client_id, symbol=symbol, side="BUY", qty=qty, trace_id=trace_id)
    ctx.write("gateway.log", "INFO", ms=920, service="gateway", host="gateway-host-1", pid=9201,
              component="ingress", event="order_received", order_id=order_id, client_id=client_id, symbol=symbol, trace_id=trace_id)
    ctx.write("gateway.log", "INFO", ms=940, service="gateway", host="gateway-host-1", pid=9201,
              component="refdata", event="vendor_lookup_start", order_id=order_id, vendor="refdata-vendor-api",
              symbol=symbol, cache_hit="false", trace_id=trace_id)
    ctx.write("gateway.log", "WARN", ms=1940, service="gateway", host="gateway-host-1", pid=9201,
              component="refdata", event="vendor_retry", order_id=order_id, vendor="refdata-vendor-api", attempt=1, backoff_ms=500, trace_id=trace_id)
    ctx.write("gateway.log", "ERROR", ms=4940, service="gateway", host="gateway-host-1", pid=9201,
              component="refdata", event="vendor_timeout", order_id=order_id, vendor="refdata-vendor-api",
              waited_ms=4000, threshold_ms=4000, trace_id=trace_id)
    ctx.write("gateway.log", "WARN", ms=4960, service="gateway", host="gateway-host-1", pid=9201,
              component="egress", event="reject_to_client", order_id=order_id, status="REJECTED", reason="REFDATA_TIMEOUT", trace_id=trace_id)
    ctx.write("client.log", "WARN", ms=4980, service="client", host="client-host-1", pid=9101,
              component="order", event="order_reject_received", order_id=order_id, reason="REFDATA_TIMEOUT", trace_id=trace_id)
    # Cached symbol passes
    ctx.write("client.log", "INFO", ms=5100, service="client", host="client-host-1", pid=9101,
              component="order", event="order_send", order_id="O2021", client_id=client_id, symbol="AAPL", side="BUY", qty=50, trace_id="T-O2021")
    ctx.write("gateway.log", "INFO", ms=5120, service="gateway", host="gateway-host-1", pid=9201,
              component="refdata", event="vendor_lookup_start", order_id="O2021", vendor="refdata-vendor-api", symbol="AAPL", cache_hit="true")
    ctx.write("gateway.log", "INFO", ms=5140, service="gateway", host="gateway-host-1", pid=9201,
              component="router", event="order_routed", order_id="O2021", route="risk", latency_ms=18, trace_id="T-O2021")


SCENARIO_BUILDERS = {
    1: scenario_1_happy_path,
    2: scenario_2_risk_reject,
    3: scenario_3_gateway_timeout,
    4: scenario_4_missing_execution_report,
    5: scenario_5_duplicate_fill_position_wrong,
    6: scenario_6_slow_order_latency,
    7: scenario_7_dns_issue,
    8: scenario_8_firewall_blocked,
    9: scenario_9_process_down,
    10: scenario_10_bad_deploy,
    11: scenario_11_consumer_lag,
    12: scenario_12_duplicate_idempotency,
    13: scenario_13_gc_latency,
    14: scenario_14_db_pool_exhaustion,
    15: scenario_15_exchange_disconnect,
    16: scenario_16_clock_skew,
    17: scenario_17_disk_full,
    18: scenario_18_permission_auth,
    19: scenario_19_partial_outage_lb,
    20: scenario_20_vendor_timeout,
}


def seed_background_noise(ctx):
    generate_health_checks(ctx, 3 if ctx.difficulty == "easy" else 6)
    if ctx.difficulty != "easy":
        generate_misleading_warnings(ctx, 4 if ctx.difficulty == "medium" else 8)
    noise_orders = 2 if ctx.difficulty == "easy" else (8 if ctx.difficulty == "medium" else 15)
    for i in range(noise_orders):
        generate_noise_order(ctx, 200 + i)


def build_logs(scenario_number, difficulty="medium"):
    ctx = LogContext(scenario_number, difficulty)
    seed_background_noise(ctx)
    SCENARIO_BUILDERS[scenario_number](ctx)
    pad_logs_to_difficulty(ctx)
    return ctx.logs


def write_logs(log_dir, logs):
    os.makedirs(log_dir, exist_ok=True)
    for file_name in LOG_FILES:
        with open(os.path.join(log_dir, file_name), "w", encoding="utf-8") as fh:
            for line in logs[file_name]:
                fh.write(line + "\n")


def print_answer_key(scenario_number):
    meta = SCENARIO_META[scenario_number]
    print(f"scenario={scenario_number}")
    print(f"title={meta['title']}")
    print(f"root_cause_category={meta['category']}")
    affected = meta["affected"]
    for key, value in affected.items():
        print(f"affected_{key}={value}")


def parse_args():
    parser = argparse.ArgumentParser(description="Generate deterministic trading-system logs for debugging practice.")
    parser.add_argument("--scenario", type=int, choices=range(1, 21), help="Scenario number to generate (1-20).")
    parser.add_argument("--random", action="store_true", help="Pick a random scenario and generate logs.")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], default="medium",
                        help="Log volume and noise level (default: medium).")
    parser.add_argument("--answer-key", action="store_true", dest="answer_key",
                        help="Print concise answer key (scenario, title, category, affected IDs) and exit.")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.answer_key:
        if not args.scenario:
            raise SystemExit("--answer-key requires --scenario <N>.")
        print_answer_key(args.scenario)
        return

    if bool(args.scenario) == bool(args.random):
        raise SystemExit("Use exactly one of --scenario <1-20> or --random.")

    log_dir = os.path.join(os.path.dirname(__file__), "logs")

    if args.random:
        chosen = random.randint(1, 20)
        logs = build_logs(chosen, args.difficulty)
        write_logs(log_dir, logs)
        print(f"Generated random practice logs in logs/ (scenario hidden, difficulty={args.difficulty}).")
        return

    logs = build_logs(args.scenario, args.difficulty)
    write_logs(log_dir, logs)
    total = sum(len(v) for v in logs.values())
    print(f"Generated scenario {args.scenario} logs in logs/ (difficulty={args.difficulty}, total_lines={total}).")


if __name__ == "__main__":
    main()
