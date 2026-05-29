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


def ts(base, ms):
    value = base + timedelta(milliseconds=ms)
    return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(value.microsecond / 1000):03d}Z"


def append(logs, file_name, line):
    logs[file_name].append(line)


def noisy_background(logs, base):
    append(logs, "system.log", f"{ts(base, 0)} INFO host=node-a cpu_pct=34 mem_pct=58 disk_pct=61")
    append(logs, "system.log", f"{ts(base, 120)} WARN ntp_offset_ms=220 source=time-sync-2")
    append(logs, "system.log", f"{ts(base, 210)} INFO connectivity check=md-feed status=ok latency_ms=12")
    append(logs, "system.log", f"{ts(base, 290)} WARN symbol_map stale_entries=1 symbol=BRK.B mapped_to=BRKB")
    append(logs, "gateway.log", f"{ts(base, 340)} INFO healthcheck route=/ping status=200 latency_ms=3")
    append(logs, "execution_publisher.log", f"{ts(base, 410)} INFO publisher heartbeat status=ok lag_ms=4")
    append(logs, "position.log", f"{ts(base, 510)} INFO snapshot client_id=C900 symbol=MSFT position=120")


def common_order_context(logs, base, order_id, client_id, symbol, qty):
    append(
        logs,
        "client.log",
        f"{ts(base, 900)} INFO order_send order_id={order_id} client_id={client_id} symbol={symbol} qty={qty} side=BUY",
    )
    append(
        logs,
        "gateway.log",
        f"{ts(base, 920)} INFO order_received order_id={order_id} client_id={client_id} symbol={symbol} qty={qty} ingress_latency_ms=6",
    )
    append(
        logs,
        "gateway.log",
        f"{ts(base, 940)} INFO order_routed order_id={order_id} route=risk svc=risk-v1 trace_id=T-{order_id}",
    )


def scenario_1_happy_path(logs, base):
    order_id = "O1001"
    client_id = "C101"
    symbol = "AAPL"
    qty = 100
    common_order_context(logs, base, order_id, client_id, symbol, qty)
    append(
        logs,
        "risk.log",
        f"{ts(base, 980)} INFO risk_eval order_id={order_id} client_id={client_id} symbol={symbol} qty={qty} decision=ACCEPT reason=within_limits",
    )
    append(logs, "gateway.log", f"{ts(base, 1015)} INFO ack_to_client order_id={order_id} status=ACK latency_ms=115")
    append(logs, "engine.log", f"{ts(base, 1080)} INFO order_accepted order_id={order_id} book={symbol} status=NEW")
    append(logs, "engine.log", f"{ts(base, 1220)} INFO fill_generated order_id={order_id} exec_id=E5001 qty=100 px=188.42")
    append(
        logs,
        "execution_publisher.log",
        f"{ts(base, 1255)} INFO execution_published order_id={order_id} exec_id=E5001 status=FILLED publish_latency_ms=5",
    )
    append(
        logs,
        "position.log",
        f"{ts(base, 1295)} INFO position_update client_id={client_id} order_id={order_id} symbol={symbol} delta=100 new_position=220",
    )
    append(logs, "client.log", f"{ts(base, 1320)} INFO execution_received order_id={order_id} exec_id=E5001 status=FILLED")
    append(logs, "system.log", f"{ts(base, 1370)} INFO svc=gateway process_state=up worker_count=8 queue_depth=2")


def scenario_2_risk_reject(logs, base):
    order_id = "O2002"
    client_id = "C202"
    symbol = "TSLA"
    qty = 15000
    common_order_context(logs, base, order_id, client_id, symbol, qty)
    append(
        logs,
        "risk.log",
        f"{ts(base, 975)} WARN risk_eval order_id={order_id} client_id={client_id} symbol={symbol} qty={qty} decision=REJECT reason=max_notional_breach limit=1000000 est_notional=2782500",
    )
    append(logs, "gateway.log", f"{ts(base, 1010)} WARN order_rejected order_id={order_id} source=risk code=RISK_LIMIT")
    append(logs, "gateway.log", f"{ts(base, 1030)} INFO reject_to_client order_id={order_id} status=REJECTED latency_ms=128")
    append(logs, "client.log", f"{ts(base, 1060)} WARN order_reject_received order_id={order_id} reason=RISK_LIMIT")
    append(logs, "engine.log", f"{ts(base, 1200)} INFO heartbeat partitions=16 status=ok")


def scenario_3_gateway_timeout(logs, base):
    order_id = "O3003"
    client_id = "C303"
    symbol = "NVDA"
    qty = 250
    common_order_context(logs, base, order_id, client_id, symbol, qty)
    append(
        logs,
        "gateway.log",
        f"{ts(base, 965)} INFO call_risk order_id={order_id} timeout_ms=150 downstream=risk-v1",
    )
    append(logs, "risk.log", f"{ts(base, 980)} INFO request_received order_id={order_id} processing_ms=240")
    append(
        logs,
        "gateway.log",
        f"{ts(base, 1118)} ERROR risk_timeout order_id={order_id} waited_ms=153 action=reject_downstream_timeout",
    )
    append(logs, "gateway.log", f"{ts(base, 1133)} WARN reject_to_client order_id={order_id} status=REJECTED reason=DOWNSTREAM_TIMEOUT")
    append(logs, "risk.log", f"{ts(base, 1220)} INFO risk_eval order_id={order_id} decision=ACCEPT reason=within_limits")
    append(logs, "system.log", f"{ts(base, 1080)} WARN svc=risk p95_latency_ms=232 threshold_ms=150")


def scenario_4_missing_execution_report(logs, base):
    order_id = "O4004"
    client_id = "C404"
    symbol = "MSFT"
    qty = 80
    common_order_context(logs, base, order_id, client_id, symbol, qty)
    append(logs, "risk.log", f"{ts(base, 980)} INFO risk_eval order_id={order_id} decision=ACCEPT reason=within_limits")
    append(logs, "gateway.log", f"{ts(base, 1015)} INFO ack_to_client order_id={order_id} status=ACK latency_ms=108")
    append(logs, "engine.log", f"{ts(base, 1180)} INFO fill_generated order_id={order_id} exec_id=E5404 qty=80 px=421.11")
    append(
        logs,
        "execution_publisher.log",
        f"{ts(base, 1210)} ERROR publish_failed order_id={order_id} exec_id=E5404 error=kafka_topic_not_found topic=exec.reports.v2",
    )
    append(
        logs,
        "execution_publisher.log",
        f"{ts(base, 1250)} WARN retry_scheduled order_id={order_id} exec_id=E5404 retry_in_ms=5000 attempt=1",
    )
    append(logs, "client.log", f"{ts(base, 1500)} WARN pending_execution order_id={order_id} waited_ms=600")
    append(logs, "system.log", f"{ts(base, 1220)} ERROR svc=execution_publisher process_state=up dependency=kafka topic_missing=exec.reports.v2")


def scenario_5_duplicate_fill_position_wrong(logs, base):
    order_id = "O5005"
    client_id = "C505"
    symbol = "AMZN"
    qty = 40
    common_order_context(logs, base, order_id, client_id, symbol, qty)
    append(logs, "risk.log", f"{ts(base, 980)} INFO risk_eval order_id={order_id} decision=ACCEPT reason=within_limits")
    append(logs, "gateway.log", f"{ts(base, 1015)} INFO ack_to_client order_id={order_id} status=ACK latency_ms=97")
    append(logs, "engine.log", f"{ts(base, 1160)} INFO fill_generated order_id={order_id} exec_id=E5505 qty=40 px=171.70")
    append(logs, "execution_publisher.log", f"{ts(base, 1185)} INFO execution_published order_id={order_id} exec_id=E5505 status=FILLED")
    append(logs, "position.log", f"{ts(base, 1210)} INFO position_update client_id={client_id} symbol={symbol} exec_id=E5505 delta=40 new_position=90")
    append(logs, "execution_publisher.log", f"{ts(base, 1240)} WARN duplicate_publish order_id={order_id} exec_id=E5505 cause=retry_without_idempotency_guard")
    append(logs, "position.log", f"{ts(base, 1265)} ERROR position_update client_id={client_id} symbol={symbol} exec_id=E5505 delta=40 new_position=130 anomaly=duplicate_exec_applied")
    append(logs, "client.log", f"{ts(base, 1290)} INFO execution_received order_id={order_id} exec_id=E5505 status=FILLED duplicate=true")


def scenario_6_slow_order_latency(logs, base):
    order_id = "O6006"
    client_id = "C606"
    symbol = "META"
    qty = 120
    common_order_context(logs, base, order_id, client_id, symbol, qty)
    append(logs, "gateway.log", f"{ts(base, 955)} WARN queue_enqueue order_id={order_id} queue=gateway_to_risk depth=1840")
    append(logs, "system.log", f"{ts(base, 970)} WARN svc=gateway queue=gateway_to_risk backlog=1840")
    append(logs, "system.log", f"{ts(base, 975)} WARN svc=gateway process=worker-3 state=down restart_count=4")
    append(logs, "risk.log", f"{ts(base, 1760)} INFO risk_eval order_id={order_id} decision=ACCEPT reason=within_limits processing_ms=8")
    append(logs, "gateway.log", f"{ts(base, 1820)} INFO ack_to_client order_id={order_id} status=ACK latency_ms=920")
    append(logs, "engine.log", f"{ts(base, 1950)} INFO fill_generated order_id={order_id} exec_id=E5606 qty=120 px=495.80")
    append(logs, "execution_publisher.log", f"{ts(base, 1985)} INFO execution_published order_id={order_id} exec_id=E5606 status=FILLED")
    append(logs, "position.log", f"{ts(base, 2015)} INFO position_update client_id={client_id} symbol={symbol} delta=120 new_position=340")
    append(logs, "client.log", f"{ts(base, 2030)} WARN slow_ack_observed order_id={order_id} ack_latency_ms=920")


SCENARIO_BUILDERS = {
    1: scenario_1_happy_path,
    2: scenario_2_risk_reject,
    3: scenario_3_gateway_timeout,
    4: scenario_4_missing_execution_report,
    5: scenario_5_duplicate_fill_position_wrong,
    6: scenario_6_slow_order_latency,
}


def build_logs(scenario_number):
    base = datetime(2026, 5, 28, 10, 0, 0, tzinfo=timezone.utc) + timedelta(minutes=scenario_number)
    logs = {name: [] for name in LOG_FILES}
    noisy_background(logs, base)
    SCENARIO_BUILDERS[scenario_number](logs, base)

    # Add one timestamp confusion hint in every scenario.
    append(
        logs,
        "system.log",
        f"{ts(base, 3000)} WARN timezone_mismatch svc=client local_ts=2026-05-28T18:00:03+08:00 utc_ts={ts(base, 3000)}",
    )
    return logs


def write_logs(log_dir, logs):
    os.makedirs(log_dir, exist_ok=True)
    for file_name in LOG_FILES:
        with open(os.path.join(log_dir, file_name), "w", encoding="utf-8") as fh:
            for line in logs[file_name]:
                fh.write(line + "\n")


def parse_args():
    parser = argparse.ArgumentParser(description="Generate deterministic trading-system logs for debugging practice.")
    parser.add_argument("--scenario", type=int, choices=range(1, 7), help="Scenario number to generate (1-6).")
    parser.add_argument("--random", action="store_true", help="Pick a random scenario and generate logs (hidden).")
    return parser.parse_args()


def main():
    args = parse_args()
    if bool(args.scenario) == bool(args.random):
        raise SystemExit("Use exactly one of --scenario <1-6> or --random.")

    if args.random:
        chosen = random.randint(1, 6)
        logs = build_logs(chosen)
        write_logs(os.path.join(os.path.dirname(__file__), "logs"), logs)
        print("Generated random practice logs in logs/.")
        return

    logs = build_logs(args.scenario)
    write_logs(os.path.join(os.path.dirname(__file__), "logs"), logs)
    print(f"Generated scenario {args.scenario} logs in logs/.")


if __name__ == "__main__":
    main()
