from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


ORDER_STATES = (
    "RECEIVED",
    "VALIDATED",
    "RISK_ACCEPTED",
    "RISK_REJECTED",
    "ROUTED",
    "ACKED",
    "REJECTED",
    "FILLED",
    "PUBLISHED",
)

REJECT_REASONS = (
    "BAD_QTY",
    "BAD_PRICE",
    "SYMBOL_DISABLED",
    "UNKNOWN_CLIENT",
    "SYMBOL_NOT_ALLOWED",
    "LIMIT_EXCEEDED",
    "DUPLICATE_ORDER_ID",
    "ROUTE_NOT_FOUND",
)


@dataclass
class OrderRequest:
    order_id: str
    client_id: str
    symbol: str
    side: str
    qty: int
    price: float
    request_id: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrderRequest":
        return cls(
            order_id=data["order_id"],
            client_id=data["client_id"],
            symbol=data["symbol"],
            side=data.get("side", "BUY"),
            qty=int(data["qty"]),
            price=float(data["price"]),
            request_id=data.get("request_id", data["order_id"]),
        )


@dataclass
class OrderResult:
    order_id: str
    request_id: str
    client_id: str
    symbol: str
    final_state: str
    success: bool
    reason: str | None = None
    notional: float | None = None
    exec_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
