from collections import defaultdict

class OrderEventTracker:
    def __init__(self):
        self.orders = {}
        self.open_orders = {}
        self.positions = defaultdict(int)
        self.invalid_events = []

    def process_event(self, event):
        event_type = event[0]

        match event_type:
            case "NEW":
                self.process_new(event)
            case "FILL":
                self.process_fill(event)
            case "CANCEL":
                self.process_cancel(event)
            case "REJECT":
                self.process_reject(event)
            case _:
                self.invalid_events.append((event, "Unknown event type"))

    def process_new(self, event):
        # ("NEW", order_id, symbol, side, qty, price)
        if len(event) != 6:
            self.invalid_events.append(event, "Malformed NEW event")
            return

        _, order_id, symbol, side, qty, price = event

        if order_id in self.orders:
            self.invalid_events.append(event, "Duplicate order_id")
            return
        
        if qty < 0 or price < 0:
            self.invalid_events.append(event, "Invalid quantity or price")
            return
        
        order = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "price": price,
            "filled_qty": 0,
            "status": "OPEN",
        }

        self.orders[order_id] = order
        self.open_orders[order_id] = order

        return True


    def process_fill(self, event):
        # ("FILL", order_id, fill_qty, fill_price)
        if len(event) != 4:
            return self.invalid_events.append(event, "Malformed FILL event")
        
        _, order_id, fill_qty, fill_price = event

        if order_id not in self.orders:
            return self.invalid_events.append(event, "Fill for unknown order")

        order = self.orders[order_id]

        if order["status"] not in {"OPEN", "PARTIALLY_FILLED"}:
            return self.invalid_events.append(event, f"Fill for non-open order: {order["status"]}")
        
        if fill_qty <= 0 or fill_price <= 0:
            return self.invalid_events.append(event, "Invalid fill quantity or price")

        remaining_qty = order["qty"] - order["filled_qty"]

        if fill_qty > remaining_qty:
            return self.invalid_events.append(event, "Fill quantity exceeds remaining quantity")
        
        # Update filled quantity
        order["filled_qty"] += fill_qty

        # Update position
        symbol = order["symbol"]

        if order["side"] == "BUY":
            self.positions[symbol] += fill_qty
        else:
            self.position[symbol] -= fill_qty

        # Update order status
        if order["filled_qty"] == order["qty"]:
            order["status"] = "FILLED"

            if  order_id in self.open_orders:
                del self.open_orders[order_id]
        
        else:
            order["status"] = "PARTIALLY_FILLED"
        
        return True

    
    def process_cancel(self, event):
        # ("CANCEL", order_Id)
        if len(event) != 2:
            return self.invalid_events.append(event, "Malformed CANCEL event")
        
        _, order_id = event

        if order_id not in self.orders:
            return self.invalid_events.append(event, "Cancel for unknown order")
        
        order = self.orders[order_id]

        if order["status"] == "FILLED":
            return self.invalid_events.append(event, "Cancel after full fill")
        
        if order["status"] == "CANCELLED":
            return self.invalid_events.append(event, "Duplicate cancel")
        
        if order["status"] == "REJECTED":
            return self.invalid_events.append(event, "Cancel rejected order")
        
        order["status"] = "CANCELLED"

        if order_id in self.open_orders:
            del self.open_orders[order_id]
        
        return True

    
    def process_reject(self, event):
        # ("REJECT", order_id, reason)
        if len(event) != 3:
            return self.invalid_events(event, "Malformed REJECT event")
        
        _, order_id, reason = event

        if order_id not in self.orders:
            self.orders[order_id] = {
                "order_id": order_id,
                "symbol": None,
                "side": None,
                "qty": 0,
                "price": None,
                "filled_qty": 0,
                "status": "REJECTED",
                "reason": reason,
            }
            return True
        
        order = self.orders[order_id]

        if order["status"] in {"FILLED", "PARTIALLY_FILLED", "CANCELLED"}:
            return self.invalid_events(event, f"Reject after order already {order['status']}")
        
        order["status"] = "REJECTED"
        order["reason"] = reason
    
        if order_id in self.open_orders:
            del self.open_orders[order_id]
        
        return True


    def get_open_orders(self):
        return self.open_orders

    def get_positions(self):
        return dict(self.positions)

    def get_invalid_events(self):
        return self.invalid_events

    def get_orders(self):
        return self.orders


### Test class above

events = [
    ("NEW", "O1", "ABC", "BUY", 100, 15.0),
    ("FILL", "O1", 40, 15.0),
    ("FILL", "O1", 60, 15.0),
]

tracker = OrderEventTracker()

for event in events:
    tracker.process_event(event)

print("Orders:")
print(tracker.get_orders())

print("Open orders:")
print(tracker.get_open_orders())

print("Positions:")
print(tracker.get_positions())

print("Invalid events:")
print(tracker.get_invalid_events())