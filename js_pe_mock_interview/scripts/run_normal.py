#!/usr/bin/env python3
"""Run the normal (bug-free) order flow."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from trading_system.pipeline import run_from_file  # noqa: E402


def main() -> None:
    results = run_from_file(ROOT, "orders_normal.jsonl", seed=42)
    ok = sum(1 for r in results if r.success)
    print(f"Normal run complete: {ok}/{len(results)} orders succeeded.")
    print(f"Logs written to {ROOT / 'logs'}/")


if __name__ == "__main__":
    main()
