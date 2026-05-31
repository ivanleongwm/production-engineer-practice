#!/usr/bin/env python3
"""Bug A: BABA orders fail with ROUTE_NOT_FOUND (missing route in config)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from trading_system.pipeline import run_from_file  # noqa: E402


def main() -> None:
    results = run_from_file(
        ROOT,
        "orders_bug_a.jsonl",
        routes_file="routes_bug_a.json",
        seed=42,
    )
    for r in results:
        status = "OK" if r.success else f"FAIL ({r.reason})"
        print(f"  {r.order_id} {r.symbol}: {status}")
    print(f"Logs written to {ROOT / 'logs'}/")


if __name__ == "__main__":
    main()
