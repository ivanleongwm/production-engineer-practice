class OrderBook:
    def __init__(self):
        self.bids = []
        self.asks = []
        self.orders = {}
        self.trades = []
        self.invalid_events = []
        self.sequence = 0
    
    def add_order(self, order_id, side, price, qty):
        # Data Validation
        new_order = {
            "order_id": order_id,
            "side": side,
            "price": price,
            "qty": qty
        }

        current_trade_index = len(self.trades)
        
        # match current order in book
        if new_order["side"] == "BUY":
            self._match_buy_order(new_order)
        else:
            self._match_sell_order(new_order)

        # rest order in book if qty is bigger than zero after matching
        if new_order["qty"] > 0:
            self._rest_order(new_order)

        # return list of trades
        return self.trades[current_trade_index:]

    def _match_buy_order(self, incoming_order):
        while (
            incoming_order["qty"] > 0 and
            self.asks and
            incoming_order["price"] >= self.asks[0]["price"]
        ):
            resting_order = self.asks[0]

            trade_qty = min(resting_order["qty"], incoming_order["qty"])
            trade_price = resting_order["price"]

            trade = {
                "buy_order_id": incoming_order["order_id"],
                "sell_order_id": resting_order["order_id"],
                "qty": trade_qty,
                "price": trade_price,
            }

            self.trades.append(trade)

            incoming_order["qty"] -= trade_qty
            resting_order["qty"] -= trade_qty

            if resting_order["qty"] == 0 :
                self.asks.pop(0)
                del self.orders[resting_order["order_id"]]

    def _match_sell_order(self, incoming_order):
        while (
            incoming_order["qty"] > 0 and
            self.bids and
            incoming_order["price"] <= self.bids[0]["price"]
        ):
            resting_order = self.bids[0]

            trade_qty = min(resting_order["qty"], incoming_order["qty"])
            trade_price = resting_order["price"]

            trade = {
                "buy_order_id": resting_order["order_id"],
                "sell_order_id": incoming_order["order_id"],
                "qty": trade_qty,
                "price": trade_price,
            }

            self.trades.append(trade)

            incoming_order["qty"] -= trade_qty
            resting_order["qty"] -= trade_qty

            if resting_order["qty"] == 0 :
                self.bids.pop(0)
                del self.orders[resting_order["order_id"]]
    
    def _rest_order(self, incoming_order):

        self.sequence += 1

        resting_order = {
            "order_id": incoming_order["order_id"],
            "side": incoming_order["side"],
            "price": incoming_order["price"],
            "qty": incoming_order["qty"],
            "sequence": self.sequence,
        }

        if incoming_order["side"] == "BUY":
            self.bids.append(resting_order)
            self.bids.sort(key=lambda x: (-x["price"], x["sequence"]))
        else:
            self.asks.append(resting_order)
            self.asks.sort(key=lambda x: (x["price"], x["sequence"]))

        # add order to list of orders
        self.orders[resting_order["order_id"]] = resting_order

        return True

    def cancel_order(self, order_id):
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]

        if order["side"] == "BUY":
            self.bids = [
                bid for bid in
                self.bids
                if order_id != bid["order_id"]
            ]
        else:
            self.asks = [
                ask for ask in 
                self.asks
                if order_id != ask["order_id"]
            ]
        
        del self.orders[order_id]

        return True

    def get_best_bid(self):
        if not self.bids:
            return None
        best_price = self.bids[0]["price"]
        total_qty = 0
        for bid in self.bids:
            if bid["price"] == best_price:
                total_qty += bid["qty"]
            else:
                break
        return best_price, total_qty

    def get_best_ask(self):
        if not self.asks:
            return None
        best_price = self.asks[0]["price"]
        total_qty = 0
        for ask in self.asks:
            if ask["price"] == best_price:
                total_qty += ask["qty"]
            else:
                break
        return best_price, total_qty