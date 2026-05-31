from __future__ import annotations

from .config_loader import ConfigBundle
from .logger import LogManager
from .models import OrderRequest, REJECT_REASONS


class Gateway:
    """Ingress point: basic validation and request forwarding."""

    def __init__(self, logs: LogManager, config: ConfigBundle) -> None:
        self.log = logs.get("gateway")
        self.config = config

    def receive(self, order: OrderRequest) -> tuple[bool, str | None]:
        self.log.info(
            "order_received",
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            qty=order.qty,
            price=order.price,
            state="RECEIVED",
        )

        if order.qty <= 0:
            self._reject(order, "BAD_QTY", "quantity must be positive")
            return False, "BAD_QTY"
        if order.price <= 0:
            self._reject(order, "BAD_PRICE", "price must be positive")
            return False, "BAD_PRICE"

        symbol_cfg = self.config.symbols.get(order.symbol)
        if not symbol_cfg:
            self._reject(order, "SYMBOL_DISABLED", "symbol not configured")
            return False, "SYMBOL_DISABLED"
        if not symbol_cfg.get("enabled", True):
            self._reject(order, "SYMBOL_DISABLED", "symbol disabled")
            return False, "SYMBOL_DISABLED"

        client_cfg = self.config.clients.get(order.client_id)
        if not client_cfg:
            self._reject(order, "UNKNOWN_CLIENT", "client not registered")
            return False, "UNKNOWN_CLIENT"

        allowed = client_cfg.get("allowed_symbols", [])
        if allowed and order.symbol not in allowed:
            self._reject(order, "SYMBOL_NOT_ALLOWED", "client not entitled for symbol")
            return False, "SYMBOL_NOT_ALLOWED"

        self.log.info(
            "forward_to_order_service",
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            state="VALIDATED",
        )
        return True, None

    def _reject(self, order: OrderRequest, reason: str, detail: str) -> None:
        assert reason in REJECT_REASONS
        self.log.warn(
            "ingress_reject",
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            state="REJECTED",
            reason=reason,
            detail=detail,
        )

    def ack_to_client(self, order: OrderRequest, state: str, reason: str | None = None) -> None:
        level = "warn" if state == "REJECTED" else "info"
        fields = dict(
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            state=state,
        )
        if reason:
            fields["reason"] = reason
        getattr(self.log, level)("ack_to_client", **fields)
