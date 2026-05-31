from __future__ import annotations

from .logger import LogManager
from .models import OrderRequest


class PositionService:
    """Maintains client positions from published executions."""

    def __init__(self, logs: LogManager) -> None:
        self.log = logs.get("position_service")
        self._positions: dict[tuple[str, str], int] = {}

    def apply_fill(self, order: OrderRequest, exec_id: str) -> None:
        key = (order.client_id, order.symbol)
        delta = order.qty if order.side.upper() == "BUY" else -order.qty
        new_pos = self._positions.get(key, 0) + delta
        self._positions[key] = new_pos
        self.log.info(
            "position_update",
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            exec_id=exec_id,
            delta=delta,
            new_position=new_pos,
        )

    def emit_reconcile_noise(self) -> None:
        self.log.info(
            "reconcile_pass",
            client_id="C10",
            symbol="AAPL",
            drift_shares=0,
            status="within_tolerance",
        )
