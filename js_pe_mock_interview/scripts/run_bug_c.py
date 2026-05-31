#!/usr/bin/env python3
"""Bug C: order_service records ACKED before matching_engine confirms; duplicate retry inconsistent."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from trading_system.pipeline import run_from_file  # noqa: E402


def main() -> None:
    results = run_from_file(
        ROOT,
        "orders_bug_c.jsonl",
        early_accept_bug=True,
        seed=42,
    )
    for r in results:
        status = "OK" if r.success else f"FAIL ({r.reason})"
        db_state = r.details.get("order_service_state", "n/a")
        print(f"  {r.order_id} request={r.request_id}: {status} (order_service_db={db_state})")
    print(f"Logs written to {ROOT / 'logs'}/")
    print("Hint: compare order_service audit lines for ORD-C01 retry vs matching_engine duplicate reject.")


if __name__ == "__main__":
    main()
