"""
Key Invariants

Bids are sorted highest price first.
Asks are sorted lowest price first.
Within the same price, earlier orders have priority.
A trade only happens when prices cross.
Trade price is the resting order price.
Fully filled orders are removed from the book.
Unfilled quantity rests in the book.

"""


from collections import defaultdict

class OrderBook:

    def __init__(self):
        self.bids = []           # BUY orders, highest price first
        self.asks = []           # SELL orders, lowest price first
        self.orders = {}         # order_id -> order
        self.trades = []         # list of executed trades
        self.sequence = 0        # used for FIFO priority within same price

    def add_order(self, order_id, side, price, qty):
        if order_id in self.orders:
            raise ValueError(f"Duplicate order_id: {order_id}")
        if side not in {"BUY","SELL"}:
            raise ValueError(f"Invalid side: {side}")
        if price <= 0 or qty <= 0:
            raise ValueError(f"Price and Quantity must be positive")

        incoming_order = {
            "order_id": order_id,
            "side": side,
            "price": price,
            "qty": qty
        }

        trade_start_index = len(self.trades)

        if side == "BUY":
            self._match_buy_order(incoming_order)
        else:
            self._match_sell_order(incoming_order)

        # If not fully filled, rest remaining qty in book
        if incoming_order["qty"] > 0:
            self._rest_order(incoming_order)

        # Return the trades caused by this incoming order
        return self.trades[trade_start_index:]


    def _match_buy_order(self, incoming_order):
        # But crosses if buy_price >= best_ask
        while (
            incoming_order["qty"] > 0
            and self.asks
            and incoming_order["price"] >= self.asks[0]["price"]
        ):
            resting_order = self.asks[0]
            
            trade_qty = min(incoming_order["qty"], resting_order["qty"])
            trade_price = resting_order["price"] # trade price = resting order price

            trade = {
                "buy_order_id": incoming_order["order_id"],
                "sell_order_id": resting_order["order_id"],
                "price": trade_price,
                "qty": trade_qty
            }

            self.trades.append(trade)

            incoming_order["qty"] -= trade_qty
            resting_order["qty"] -= trade_qty

            # If resting ask is fully filled, remove it
            if resting_order["qty"] == 0:
                self.asks.pop(0)
                del self.orders[resting_order["order_id"]]

    
    def _match_sell_order(self, incoming_order):
        while (
            incoming_order["qty"] > 0
            and self.bids
            and incoming_order["price"] <= self.bids[0]["price"]
        ):
            resting_order = self.bids[0]

            trade_qty = min(incoming_order["qty"], resting_order["qty"])
            trade_price = resting_order[0]["price"] # trade price = resting order price

            trade = {
                "sell_order_id": incoming_order["order_id"],
                "buy_order_id": resting_order["order_id"],
                "price": trade_price,
                "qty": trade_qty
            }

            incoming_order["qty"] -= trade_qty
            resting_order["qty"] -= trade_qty

            if resting_order["qty"] == 0:
                self.bids.pop(0)
                del self.orders[resting_order["order_id"]]


    def _rest_order(self, order):
        self.sequence += 1

        resting_order =  {
            "order_id": order["order_id"],
            "side": order["side"],
            "price": order["price"],
            "qty": order["qty"],
            "sequence": self.sequence
        }

        self.orders[resting_order["order_id"]] = resting_order

        if resting_order["side"] == "BUY":
            self.bids.append(resting_order)
            self.bids.sort(key=lambda x: (-x["price"], x["sequence"])) 
        else:
            self.asks.append(resting_order)
            self.asks.sort(key=lambda x: (x["price"], x["sequence"]))


    def cancel(self, order_id):
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]

        if order["side"] == "BUY":
            self.bids = [
                bid for bid in self.bids
                if bid["order_id"] != order_id
            ]
        else:
            self.asks = [
                ask for ask in self.asks
                if ask["order_id"] != order_id
            ]

        del self.orders[order_id]
        return True

    
    def get_best_bid(self):
        if not self.bids:
            return None

        best_price = self.bids[0]["price"]
        total_qty = sum(
            order["qty"]
            for order in self.bids
            if order["price"] == best_price
        )

        return best_price, total_qty
    
    def get_best_ask(self):
        if not self.asks:
            return None

        best_price = self.asks[0]["price"]
        total_qty = sum(
            order["qty"]
            for order in self.asks
            if order["price"] == best_price
        )

        return best_price, total_qty

    def get_book(self):
        return {
            "bids": self.bids,
            "asks": self.asks,
        }

    def get_trades(self):
        return self.trades

print("########## Example 1: resting ask, then buy crosses ##############")

book = OrderBook()

print(book.add_order("S1", "SELL", 10.0, 100))
print("Best ask:", book.get_best_ask())

print(book.add_order("B1", "BUY", 11.0, 40))
print("Best ask:", book.get_best_ask())
print("Trades:", book.get_trades())
print("Book:", book.get_book())


print("########## Example 2: full fill removes resting order ##############"

book.add_order("B2", "BUY", 10.0, 60)

print("Best ask:", book.get_best_ask())
print("Trades:", book.get_trades())
print("Book:", book.get_book())


print("########## Example 3: buy does not cross, so it rests ############## ")

book.add_order("B3", "BUY", 9.0, 50)

print("Best bid:", book.get_best_bid())
print("Book:", book.get_book())


print("########## Example 4: sell crosses best bid ############## ")

trades = book.add_order("S2", "SELL", 8.0, 20)

print("Trades from S2:", trades)
print("Best bid:", book.get_best_bid())