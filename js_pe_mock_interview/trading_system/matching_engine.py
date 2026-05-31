from __future__ import annotations

from .logger import LogManager
from .models import OrderRequest, REJECT_REASONS


class MatchingEngine:
    """Simulated matching engine with duplicate order_id detection."""

    def __init__(self, logs: LogManager) -> None:
        self.log = logs.get("matching_engine")
        self._seen_order_ids: set[str] = set()
        self._fills: dict[str, str] = {}

    def submit(self, order: OrderRequest, route: str) -> tuple[bool, str | None, str | None]:
        if order.order_id in self._seen_order_ids:
            self.log.warn(
                "duplicate_order",
                request_id=order.request_id,
                order_id=order.order_id,
                client_id=order.client_id,
                symbol=order.symbol,
                state="REJECTED",
                reason="DUPLICATE_ORDER_ID",
                route=route,
            )
            return False, "DUPLICATE_ORDER_ID", None

        self._seen_order_ids.add(order.order_id)
        exec_id = f"EXEC-{order.order_id}"
        self._fills[order.order_id] = exec_id
        self.log.info(
            "order_filled",
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            state="FILLED",
            route=route,
            exec_id=exec_id,
            fill_qty=order.qty,
            fill_price=order.price,
        )
        return True, None, exec_id
