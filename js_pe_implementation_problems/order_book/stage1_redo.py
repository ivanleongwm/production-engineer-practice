


class OrderBook:
    def __init__(self):
        self.bids = [] # highest first
        self.asks = [] # lowest first
        self.orders = {}
        self.trades = []
        self.sequence = 0

    def add_order(self, order_id, side, price, qty):

        # add to orders
        new_order = {
            "order_id": order_id,
            "side": side,
            "qty": qty,
            "price": price,
        }

        self.orders[order_id] = new_order

        trade_start_index = len(self.trades)

        # match order in book
        if new_order["side"] == "BUY":
            self._match_buy_order(new_order)
        else:
            self._match_sell_order(new_order)

        # rest order in book
        if new_order["qty"] > 0:
            self._rest_order(new_order)

        # return trades resulting from order
        return self.trades[trade_start_index:]



    def _match_buy_order(self, incoming_order):
        while (
            incoming_order["qty"] > 0 and
            self.asks and
            incoming_order["price"] >= self.asks[0]["price"]
        ):
            resting_order = self.asks[0]

            trade_qty = min(incoming_order["qty"], resting_order["qty"])
            trade_price = asks[0]["price"]

            trade = {
                "buy_order_id": incoming_order["order_id"],
                "sell_order_id": resting_order["order_id"],
                "price": trade_price,
                "qty": trade_qty
            }

            self.trades.append(trade)

            incoming_order["qty"] -= trade_qty
            resting_order["qty"] -= trade_qty

            # if resting order is fully filled, delete it
            if resting_order["qty"] == 0:
                self.asks.pop(0)
                del self.orders[resting_order["order_id"]]

    def _match_sell_order(self, incoming_order):
        while (
            incoming_order["qty"] > 0 and
            self.bids and
            incoming_order["price"] <= self.bids[0]
        ):

            resting_order = self.bids[0]

            trade_qty = min(resting_order["qty"], incoming_order["qty"])
            trade_price = resting_order["price"]

            trade = {
                "buy_order_id": resting_order["order_id"],
                "sell_order_id": incoming_order["order_id"],
                "qty": trade_qty,
                "price": trade_price
            }

            self.trades.append(trade)

            resting_order["qty"] -= trade_qty
            incoming_order["qty"] -= trade_qty

            if resting_order["qty"] == 0:
                self.bids.pop(0)
                del self.orders[resting_order["order_id"]]

    def _rest_order(self, incoming_order):
        self.sequence += 1

        resting_order = {
            "order_id": incoming_order["order_id"],
            "side": incoming_order["side"],
            "qty": incoming_order["qty"],
            "sequence": self.sequence
        }

        # add order to list of orders
        self.orders[resting_order["order_id"]] = resting_order

        # rest order in book
        if incoming_order["side"] == "BUY":
            self.bids.append(incoming_order)
            self.bids.sort(key=lambda x: (-x["price"], x["sequence"]))
        else:
            self.asks.append(incoming_order)
            self.asks.sort(key=lambda x: (x["price"], x["sequence"]))


    def cancel_order(self, order_id):
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]

        # remove order from book
        if order["side"] == "BUY":
            self.bids = [
                bid for bid in 
                self.bids
                if bid["order_id"] != order_id
            ]
        else:
            order["side"] == "SELL":
            self.asks = [
                ask for ask in
                self.asks
                if ask["order_id"] != order_id
            ]

        # delete order from list of orders    
        del self.orders[order_id]
        return = true
        

    def get_best_bid(self):
        if not self.bids:
            return None
        best_price = self.bids[0]["price"]
        total_qty = sum(
            [
                bid for bid in
                self.bids
                if bid["price"] == best_price
            ]
        )
        return best_price, total_qty

    def get_best_ask(self):
        if not self.asks:
            return None
        best_price = self.asks[0]["price"]
        total_qty = sum(
            [
                ask for ask in
                self.asks
                if ask["price"] == bset_price
            ]
        )

    def get_book(self):
        return {
            "bids": self.bids,
            "asks": self.asks
        }

    def get_trades(self):
        return self.trades