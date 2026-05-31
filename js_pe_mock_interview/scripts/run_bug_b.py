#!/usr/bin/env python3
"""Bug B: C21 hits LIMIT_EXCEEDED at exact notional boundary (>= bug)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from trading_system.pipeline import run_from_file  # noqa: E402


def main() -> None:
    results = run_from_file(
        ROOT,
        "orders_bug_b.jsonl",
        inclusive_limit_bug=True,
        seed=42,
    )
    for r in results:
        status = "OK" if r.success else f"FAIL ({r.reason})"
        extra = f" notional={r.notional}" if r.notional else ""
        print(f"  {r.order_id} client={r.client_id}{extra}: {status}")
    print(f"Logs written to {ROOT / 'logs'}/")


if __name__ == "__main__":
    main()
