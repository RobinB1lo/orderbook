import bisect
from .models import Side, Type, Order, Trade


class OrderBook:
    def __init__(self):
        self.asks = {}
        self.bids = {}
        self.ask_prices = []
        self.bid_prices = []
        self.orders = {}

    def fill_order(self, order):
        if order.get_order_side() == Side.BUY:
            return self.process_buy_order(order)
        elif order.get_order_side() == Side.SELL:
            return self.process_sell_order(order)
        else:
            raise ValueError("Invalid order side")

    def process_buy_order(self, order):
        remaining_quantity = order.remaining_quantity

        if order.get_order_type() == Type.FOK:
            total_available = self.calculate_available_asks(order.get_order_price())
            if total_available < remaining_quantity:
                return False

        while remaining_quantity > 0 and self.ask_prices:
            best_ask = self.ask_prices[0]

            if (
                order.get_order_type() == Type.LIMIT
                and best_ask > order.get_order_price()
            ):
                break

            orders_at_price = self.asks[best_ask]
            while orders_at_price and remaining_quantity > 0:
                curr_ask = orders_at_price[0]
                trade_quantity = min(curr_ask.remaining_quantity, remaining_quantity)

                self._execute_trade(curr_ask.order_price, trade_quantity, order.order_type)

                curr_ask.remaining_quantity -= trade_quantity
                remaining_quantity -= trade_quantity

                if curr_ask.remaining_quantity == 0:
                    orders_at_price.pop(0)
                    self.orders.pop(curr_ask.orderID)

                if not orders_at_price:
                    self.ask_prices.pop(0)
                    del self.asks[best_ask]

                if order.get_order_type() == Type.FOK and remaining_quantity > 0:
                    return False

        if remaining_quantity > 0 and order.get_order_type() == Type.LIMIT:
            order.remaining_quantity = remaining_quantity
            self.add_bid(order)
            return True

        return remaining_quantity == 0

    def process_sell_order(self, order):
        remaining_quantity = order.remaining_quantity

        if order.get_order_type() == Type.FOK:
            total_available = self.calculate_available_bids(order.get_order_price())
            if total_available < remaining_quantity:
                return False

        while remaining_quantity > 0 and self.bid_prices:
            best_bid = self.bid_prices[0]

            if (
                order.get_order_type() == Type.LIMIT
                and best_bid < order.get_order_price()
            ):
                break

            orders_at_price = self.bids[best_bid]
            while orders_at_price and remaining_quantity > 0:
                curr_bid = orders_at_price[0]
                trade_quantity = min(curr_bid.remaining_quantity, remaining_quantity)

                self._execute_trade(curr_bid.order_price, trade_quantity, order.order_type)

                curr_bid.remaining_quantity -= trade_quantity
                remaining_quantity -= trade_quantity

                if curr_bid.remaining_quantity == 0:
                    orders_at_price.pop(0)
                    self.orders.pop(curr_bid.orderID)

            if not orders_at_price:
                self.bid_prices.pop(0)
                del self.bids[best_bid]

            if order.get_order_type() == Type.FOK and remaining_quantity > 0:
                return False

        if remaining_quantity > 0 and order.get_order_type() == Type.LIMIT:
            order.remaining_quantity = remaining_quantity
            self.add_ask(order)
            return True

        return remaining_quantity == 0

    def _execute_trade(self, price, quantity, order_type):
        trade_id = len(Trade.trade_log) + 1
        Trade(
            trade_id=trade_id,
            trade_price=price,
            trade_type=order_type,
            trade_quantity=quantity,
        )

    def calculate_available_asks(self, max_price):
        total = 0
        for price in self.ask_prices:
            if price > max_price:
                break
            total += sum(order.remaining_quantity for order in self.asks[price])
        return total

    def calculate_available_bids(self, min_price):
        total = 0
        for price in self.bid_prices:
            if price < min_price:
                break
            total += sum(order.remaining_quantity for order in self.bids[price])
        return total

    def add_bid(self, order):
        price = order.get_order_price()
        if price not in self.bids:
            index = bisect.bisect_left([-p for p in self.bid_prices], -price)
            self.bid_prices.insert(index, price)
            self.bids[price] = []
        self.bids[price].append(order)
        self.orders[order.orderID] = (price, order.order_side)

    def add_ask(self, order):
        price = order.get_order_price()
        if price not in self.asks:
            index = bisect.bisect_left(self.ask_prices, price)
            self.ask_prices.insert(index, price)
            self.asks[price] = []
        self.asks[price].append(order)
        self.orders[order.orderID] = (price, order.order_side)

    def cancel_order(self, orderID):
        if orderID not in self.orders:
            return False
        price, side = self.orders[orderID]
        del self.orders[orderID]

        if side == Side.BUY:
            order_list = self.bids.get(price, [])
            for i, order in enumerate(order_list):
                if order.orderID == orderID:
                    order_list.pop(i)
                    break
            if not order_list:
                if price in self.bids:
                    del self.bids[price]
                index = bisect.bisect_left(self.bid_prices, price)
                if index < len(self.bid_prices) and self.bid_prices[index] == price:
                    self.bid_prices.pop(index)

        elif side == Side.SELL:
            order_list = self.asks.get(price, [])
            for i, order in enumerate(order_list):
                if order.orderID == orderID:
                    order_list.pop(i)
                    break
            if not order_list:
                if price in self.asks:
                    del self.asks[price]
                index = bisect.bisect_left(self.ask_prices, price)
                if index < len(self.ask_prices) and self.ask_prices[index] == price:
                    self.ask_prices.pop(index)

        return True
