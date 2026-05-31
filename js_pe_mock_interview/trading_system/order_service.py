from __future__ import annotations

from .logger import LogManager
from .models import OrderRequest


class OrderService:
    """Order lifecycle store / audit trail (in-memory DB simulation)."""

    def __init__(self, logs: LogManager, *, early_accept_bug: bool = False) -> None:
        self.log = logs.get("order_service")
        self.early_accept_bug = early_accept_bug
        self._records: dict[str, dict] = {}

    def register(self, order: OrderRequest) -> None:
        self.log.info(
            "persist_order",
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            state="VALIDATED",
            db_table="orders",
        )
        self._records[order.order_id] = {
            "order_id": order.order_id,
            "client_id": order.client_id,
            "symbol": order.symbol,
            "state": "VALIDATED",
        }

    def mark_early_accepted(self, order: OrderRequest) -> None:
        """Bug path: mark ACCEPTED before downstream confirmation."""
        if not self.early_accept_bug:
            return
        self._records[order.order_id]["state"] = "ACKED"
        self.log.info(
            "audit_update",
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            state="ACKED",
            db_table="orders",
            note="early_accept_before_matching_engine",
        )

    def update_state(self, order: OrderRequest, state: str, reason: str | None = None) -> None:
        if order.order_id not in self._records:
            self.register(order)
        if self.early_accept_bug and self._records[order.order_id]["state"] == "ACKED" and state == "REJECTED":
            return
        self._records[order.order_id]["state"] = state
        fields = dict(
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            state=state,
            db_table="orders",
        )
        if reason:
            fields["reason"] = reason
        self.log.info("audit_update", **fields)

    def get_state(self, order_id: str) -> str | None:
        record = self._records.get(order_id)
        return record["state"] if record else None

    def snapshot(self, order_id: str) -> dict | None:
        return self._records.get(order_id)
