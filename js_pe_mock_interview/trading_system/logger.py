from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TextIO


class ComponentLogger:
    """Append-only structured logger for one simulated service."""

    _epoch = datetime(2026, 6, 2, 14, 0, 0, tzinfo=timezone.utc)
    _seq = 0

    def __init__(self, component: str, log_dir: Path) -> None:
        self.component = component
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._fh: TextIO = open(self.log_dir / f"{component}.log", "a", encoding="utf-8")

    @classmethod
    def reset_clock(cls) -> None:
        cls._epoch = datetime(2026, 6, 2, 14, 0, 0, tzinfo=timezone.utc)
        cls._seq = 0

    def _next_ts(self) -> str:
        ComponentLogger._seq += 1
        value = ComponentLogger._epoch + timedelta(milliseconds=ComponentLogger._seq * 7)
        return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(value.microsecond / 1000):03d}Z"

    def log(
        self,
        level: str,
        message: str,
        *,
        request_id: str | None = None,
        order_id: str | None = None,
        client_id: str | None = None,
        symbol: str | None = None,
        state: str | None = None,
        reason: str | None = None,
        **extra: str | int | float | bool,
    ) -> None:
        parts = [
            f"ts={self._next_ts()}",
            f"level={level}",
            f"component={self.component}",
            f"message={message}",
        ]
        if request_id:
            parts.append(f"request_id={request_id}")
        if order_id:
            parts.append(f"order_id={order_id}")
        if client_id:
            parts.append(f"client_id={client_id}")
        if symbol:
            parts.append(f"symbol={symbol}")
        if state:
            parts.append(f"state={state}")
        if reason:
            parts.append(f"reason={reason}")
        for key, value in extra.items():
            parts.append(f"{key}={value}")
        self._fh.write(" ".join(parts) + "\n")
        self._fh.flush()

    def info(self, message: str, **fields) -> None:
        self.log("INFO", message, **fields)

    def warn(self, message: str, **fields) -> None:
        self.log("WARN", message, **fields)

    def error(self, message: str, **fields) -> None:
        self.log("ERROR", message, **fields)

    def close(self) -> None:
        self._fh.close()


class LogManager:
    COMPONENTS = [
        "client_simulator",
        "gateway",
        "order_service",
        "risk_engine",
        "order_router",
        "matching_engine",
        "execution_publisher",
        "position_service",
        "system",
    ]

    def __init__(self, log_dir: Path) -> None:
        self.log_dir = log_dir
        self.loggers = {name: ComponentLogger(name, log_dir) for name in self.COMPONENTS}

    @classmethod
    def reset_logs(cls, log_dir: Path) -> None:
        log_dir.mkdir(parents=True, exist_ok=True)
        for name in cls.COMPONENTS:
            path = log_dir / f"{name}.log"
            path.write_text("", encoding="utf-8")
        ComponentLogger.reset_clock()

    def get(self, component: str) -> ComponentLogger:
        return self.loggers[component]

    def close_all(self) -> None:
        for logger in self.loggers.values():
            logger.close()
