from __future__ import annotations

import json
import random
from pathlib import Path

from .client_simulator import ClientSimulator
from .config_loader import ConfigBundle
from .execution_publisher import ExecutionPublisher
from .gateway import Gateway
from .logger import LogManager
from .matching_engine import MatchingEngine
from .models import OrderRequest, OrderResult
from .order_router import OrderRouter
from .order_service import OrderService
from .position_service import PositionService
from .risk_engine import RiskEngine


def load_orders(path: Path) -> list[OrderRequest]:
    orders: list[OrderRequest] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            orders.append(OrderRequest.from_dict(json.loads(line)))
    return orders


class TradingPipeline:
    """In-process orchestrator simulating cross-service order flow."""

    def __init__(
        self,
        root: Path,
        *,
        routes_file: str = "routes.json",
        inclusive_limit_bug: bool = False,
        early_accept_bug: bool = False,
        seed: int = 42,
    ) -> None:
        self.root = root
        self.log_dir = root / "logs"
        LogManager.reset_logs(self.log_dir)
        self.logs = LogManager(self.log_dir)
        self.config = ConfigBundle(root, routes_file=routes_file)
        self.client = ClientSimulator(self.logs, seed=seed)
        self.gateway = Gateway(self.logs, self.config)
        self.order_service = OrderService(self.logs, early_accept_bug=early_accept_bug)
        self.risk_engine = RiskEngine(
            self.logs, self.config, inclusive_limit_bug=inclusive_limit_bug
        )
        self.order_router = OrderRouter(self.logs, self.config)
        self.matching_engine = MatchingEngine(self.logs)
        self.execution_publisher = ExecutionPublisher(self.logs)
        self.position_service = PositionService(self.logs)
        self.system_log = self.logs.get("system")
        self._rng = random.Random(seed)

    def emit_system_noise(self, count: int = 5) -> None:
        services = [
            "gateway",
            "order_service",
            "risk_engine",
            "order_router",
            "matching_engine",
        ]
        for i in range(count):
            svc = services[i % len(services)]
            self.system_log.info(
                "periodic_healthcheck",
                service=svc,
                status="ok",
                cpu_pct=20 + self._rng.randint(0, 40),
                mem_pct=35 + self._rng.randint(0, 30),
            )

    def process_order(self, order: OrderRequest) -> OrderResult:
        self.client.submit(order)

        ok, reason = self.gateway.receive(order)
        if not ok:
            self.gateway.ack_to_client(order, "REJECTED", reason)
            self.client.receive_response(order, "REJECTED", reason)
            return OrderResult(
                order.order_id,
                order.request_id,
                order.client_id,
                order.symbol,
                "REJECTED",
                False,
                reason,
            )

        self.order_service.register(order)

        accepted, risk_reason, notional = self.risk_engine.evaluate(order)
        if not accepted:
            self.order_service.update_state(order, "RISK_REJECTED", risk_reason)
            self.gateway.ack_to_client(order, "REJECTED", risk_reason)
            self.client.receive_response(order, "REJECTED", risk_reason)
            return OrderResult(
                order.order_id,
                order.request_id,
                order.client_id,
                order.symbol,
                "RISK_REJECTED",
                False,
                risk_reason,
                notional=notional,
            )

        self.order_service.update_state(order, "RISK_ACCEPTED")

        routed, route_reason, route = self.order_router.route(order)
        if not routed:
            self.order_service.update_state(order, "REJECTED", route_reason)
            self.gateway.ack_to_client(order, "REJECTED", route_reason)
            self.client.receive_response(order, "REJECTED", route_reason)
            return OrderResult(
                order.order_id,
                order.request_id,
                order.client_id,
                order.symbol,
                "REJECTED",
                False,
                route_reason,
                notional=notional,
            )

        self.order_service.update_state(order, "ROUTED")

        self.order_service.mark_early_accepted(order)

        filled, fill_reason, exec_id = self.matching_engine.submit(order, route or "")
        if not filled:
            if not (self.order_service.early_accept_bug and fill_reason == "DUPLICATE_ORDER_ID"):
                self.order_service.update_state(order, "REJECTED", fill_reason)
            else:
                self.order_service.log.warn(
                    "state_inconsistency",
                    request_id=order.request_id,
                    order_id=order.order_id,
                    client_id=order.client_id,
                    symbol=order.symbol,
                    db_state=self.order_service.get_state(order.order_id),
                    downstream_state="REJECTED",
                    reason=fill_reason,
                )
            self.gateway.ack_to_client(order, "REJECTED", fill_reason)
            self.client.receive_response(order, "REJECTED", fill_reason)
            return OrderResult(
                order.order_id,
                order.request_id,
                order.client_id,
                order.symbol,
                "REJECTED",
                False,
                fill_reason,
                notional=notional,
                details={"order_service_state": self.order_service.get_state(order.order_id)},
            )

        self.order_service.update_state(order, "FILLED")
        self.execution_publisher.publish(order, exec_id or "")
        self.order_service.update_state(order, "PUBLISHED")
        self.position_service.apply_fill(order, exec_id or "")
        self.gateway.ack_to_client(order, "ACKED")
        self.client.receive_response(order, "ACKED")
        return OrderResult(
            order.order_id,
            order.request_id,
            order.client_id,
            order.symbol,
            "PUBLISHED",
            True,
            exec_id=exec_id,
            notional=notional,
        )

    def run_orders(self, orders: list[OrderRequest], *, noise: bool = True) -> list[OrderResult]:
        if noise:
            self.emit_system_noise()
            self.client.emit_background_noise()
            self.position_service.emit_reconcile_noise()

        results: list[OrderResult] = []
        for order in orders:
            results.append(self.process_order(order))
            if noise and self._rng.random() < 0.3:
                self.emit_system_noise(1)
        return results

    def close(self) -> None:
        self.logs.close_all()


def run_from_file(
    root: Path,
    orders_file: str,
    *,
    routes_file: str = "routes.json",
    inclusive_limit_bug: bool = False,
    early_accept_bug: bool = False,
    seed: int = 42,
    noise: bool = True,
) -> list[OrderResult]:
    pipeline = TradingPipeline(
        root,
        routes_file=routes_file,
        inclusive_limit_bug=inclusive_limit_bug,
        early_accept_bug=early_accept_bug,
        seed=seed,
    )
    try:
        orders = load_orders(root / "data" / orders_file)
        return pipeline.run_orders(orders, noise=noise)
    finally:
        pipeline.close()
