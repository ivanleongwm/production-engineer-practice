from __future__ import annotations

from .logger import LogManager
from .models import OrderRequest


class ExecutionPublisher:
    """Publishes fills to downstream consumers."""

    def __init__(self, logs: LogManager) -> None:
        self.log = logs.get("execution_publisher")
        self._published: set[str] = set()

    def publish(self, order: OrderRequest, exec_id: str) -> bool:
        if exec_id in self._published:
            self.log.warn(
                "duplicate_publish_skipped",
                request_id=order.request_id,
                order_id=order.order_id,
                exec_id=exec_id,
            )
            return False
        self._published.add(exec_id)
        self.log.info(
            "execution_published",
            request_id=order.request_id,
            order_id=order.order_id,
            client_id=order.client_id,
            symbol=order.symbol,
            state="PUBLISHED",
            exec_id=exec_id,
            topic="executions.v1",
        )
        return True
