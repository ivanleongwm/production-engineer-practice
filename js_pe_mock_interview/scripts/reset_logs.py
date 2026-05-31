#!/usr/bin/env python3
"""Clear all logs/ files."""

from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from trading_system.logger import LogManager  # noqa: E402


def main() -> None:
    LogManager.reset_logs(ROOT / "logs")
    print(f"Cleared logs in {ROOT / 'logs'}")


if __name__ == "__main__":
    main()
