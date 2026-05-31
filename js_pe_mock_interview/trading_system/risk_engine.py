from __future__ import annotations

from .config_loader import ConfigBundle
from .logger import LogManager
from .models import OrderRequest, REJECT_REASONS


class RiskEngine:
    """Pre-trade risk checks: client limits and symbol constraints."""

    def __init__(
        self,
        logs: LogManager,
        config: ConfigBundle,
        *,
        inclusive_limit_bug: bool = False,
    ) -> None:
        self.log = logs.get("risk_engine")
        self.config = config
        self.inclusive_limit_bug = inclusive_limit_bug

    def evaluate(self, order: OrderRequest) -> tuple[bool, str | None, float]:
        notional = order.qty * order.price
        client_cfg = self.config.clients[order.client_id]
        limit = float(client_cfg["notional_limit"])

        self.log.info(
            "risk_eval_start",
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            qty=order.qty,
            price=order.price,
            notional=round(notional, 2),
            client_limit=limit,
        )

        if self.inclusive_limit_bug:
            breach = notional >= limit
            comparator = ">="
        else:
            breach = notional > limit
            comparator = ">"

        if breach:
            self.log.warn(
                "risk_reject",
                request_id=order.request_id,
                order_id=order.order_id,
                client_id=order.client_id,
                symbol=order.symbol,
                state="RISK_REJECTED",
                reason="LIMIT_EXCEEDED",
                notional=round(notional, 2),
                client_limit=limit,
                check=f"notional {comparator} limit",
            )
            return False, "LIMIT_EXCEEDED", notional

        self.log.info(
            "risk_accept",
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            state="RISK_ACCEPTED",
            notional=round(notional, 2),
            client_limit=limit,
            check=f"notional {comparator} limit",
        )
        return True, None, notional
