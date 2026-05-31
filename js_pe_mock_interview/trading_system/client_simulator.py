from __future__ import annotations

import random
from typing import Iterable

from .logger import LogManager
from .models import OrderRequest


class ClientSimulator:
    """Simulates external clients submitting orders."""

    def __init__(self, logs: LogManager, seed: int = 42) -> None:
        self.log = logs.get("client_simulator")
        self._rng = random.Random(seed)

    def submit(self, order: OrderRequest) -> None:
        self.log.info(
            "submit_order",
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            side=order.side,
            qty=order.qty,
            price=order.price,
            state="RECEIVED",
        )

    def receive_response(self, order: OrderRequest, final_state: str, reason: str | None = None) -> None:
        fields = dict(
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            state=final_state,
        )
        if reason:
            fields["reason"] = reason
            self.log.warn("order_response", **fields)
        else:
            self.log.info("order_response", **fields)

    def emit_background_noise(self, count: int = 3) -> None:
        symbols = ["AAPL", "MSFT", "JD", "NVDA"]
        for i in range(count):
            self.log.info(
                "heartbeat",
                client_id=f"C{10 + i}",
                message_detail="session_keepalive",
                session_id=f"S-{1000 + i}",
            )
            if self._rng.random() < 0.5:
                self.log.info(
                    "unrelated_order_ack",
                    order_id=f"ORD-NOISE-{i}",
                    client_id="C10",
                    symbol=self._rng.choice(symbols),
                    state="ACKED",
                )
