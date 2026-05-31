from __future__ import annotations

from .config_loader import ConfigBundle
from .logger import LogManager
from .models import OrderRequest, REJECT_REASONS


class OrderRouter:
    """Maps symbols to routing destinations using config/routes.json."""

    VALID_VENUES = {"US_EQUITY", "HK_EQUITY", "CN_EQUITY"}

    def __init__(self, logs: LogManager, config: ConfigBundle) -> None:
        self.log = logs.get("order_router")
        self.config = config

    def route(self, order: OrderRequest) -> tuple[bool, str | None, str | None]:
        route = self.config.routes.get(order.symbol)
        if route is None:
            self.log.error(
                "route_missing",
                request_id=order.request_id,
                order_id=order.order_id,
                client_id=order.client_id,
                symbol=order.symbol,
                state="REJECTED",
                reason="ROUTE_NOT_FOUND",
                config_key=order.symbol,
                available_routes=",".join(sorted(self.config.routes.keys())),
            )
            return False, "ROUTE_NOT_FOUND", None

        if route not in self.VALID_VENUES:
            self.log.error(
                "route_invalid",
                request_id=order.request_id,
                order_id=order.order_id,
                client_id=order.client_id,
                symbol=order.symbol,
                state="REJECTED",
                reason="ROUTE_NOT_FOUND",
                configured_route=route,
                detail="unknown venue code",
            )
            return False, "ROUTE_NOT_FOUND", route

        self.log.info(
            "route_selected",
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            state="ROUTED",
            route=route,
            destination="matching_engine",
        )
        return True, None, route
