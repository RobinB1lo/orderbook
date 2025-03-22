import bisect
from enums import Side, Type
from fastapi import FastAPI

# import yfinance as yf
# import datetime as dt
# import time
# import csv


class OrderBook:
    def __init__(self):
        self.asks = {}
        self.bids = {}
        self.ask_prices = []
        self.bid_prices = []
        self.orders = {}

    def fill_order(self, order):
        if order.get_order_side() == Side.BUY:
            self.process_buy_order(order)
        elif order.get_order_side() == Side.SELL:
            self.process_sell_order(order)
        else:
            raise ValueError("Invalid order side")

    def process_buy_order(self, order):
        remaining_quantity = order.remaining_quantitiy

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

                self.execute_trade(
                    curr_ask.order_price, trade_quantity, order.order_type
                )

                curr_ask.remaining_quantity -= trade_quantity
                remaining_quantity -= trade_quantity

                if curr_ask.remaining_quantity == 0:
                    orders_at_price.pop(0)
                    self.orders.pop(curr_ask.order_id)

                if not orders_at_price:
                    self.ask_prices.pop(0)
                    del self.asks[best_ask]

                if order.get_order_type() == Type.FOK and remaining_quantity > 0:
                    return False

            if remaining_quantity > 0 and order.get_order_type() == Type.LIMIT:
                self.add_bid(order)
                order.remaining_quantity = remaining_quantity
                return True

            return remaining_quantity == 0

    def process_sell_order(self, order):
        remaining_quantity = order.remaining_quantitiy

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

                self.execute_trade(
                    curr_bid.order_price, trade_quantity, order.order_type
                )

                curr_bid.remaining_quantity -= trade_quantity
                remaining_quantity -= trade_quantity

                if curr_bid.remaining_quantity == 0:
                    orders_at_price.pop(0)
                    self.orders.pop(curr_bid.order_id)

            if not orders_at_price:
                self.bid_prices.pop(0)
                del self.bids[best_bid]

            if order.get_order_type() == Type.FOK and remaining_quantity > 0:
                return False

        if remaining_quantity > 0 and order.get_order_type() == Type.LIMIT:
            self.add_ask(order)
            order.remaining_quantity = remaining_quantity
            return True

        return remaining_quantity == 0

    def execute_trade(self, price, quantitiy):
        trade_id = len(Trade.trade_log) + 1
        Trade(trade_id, price, quantitiy)

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
        self.orders[order.orderID] = (price, "bid")

    def add_ask(self, order):
        price = order.get_order_price()
        if price not in self.asks:
            index = bisect.bisect_left(self.ask_prices, price)
            self.ask_prices.insert(index, price)
            self.asks[price] = []
        self.asks[price].append(order)
        self.orders[order.orderID] = (price, "ask")

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
            order_list = self.bids.get(price, [])

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


class Order:
    _next_orderId_ = 0

    def __init__(self, orderprice, orderquantity, type, side):
        if side not in (Side.SELL, Side.BUY):
            raise ValueError("Side must be 0 (sell) or 1 (buy)")
        if type not in (Type.FOK, Type.LIMIT, Type.MARKET):
            raise ValueError("Type must be 0 (Limit), 1 (Market), or 2 (Fill Or Kill)")
        self.orderID = Order._next_orderId_
        self.initialquantitiy = orderquantity
        self.remaining_quantitiy = orderquantity
        self.order_price = orderprice
        self.order_side = side
        self.order_type = type
        Order._next_orderId_ += 1

    def get_order_price(self):
        return self.order_price

    def get_order_type(self):
        return self.order_type

    def get_order_side(self):
        return self.order_side

    def get_order_id(self):
        return self.orderID

    def get_initial_quantitiy(self):
        return self.initialquantitiy

    def get_remaining_quantitiy(self):
        return self.remaining_quantitiy

    def get_filled_quantity(self):
        return self.initialquantitiy - self.remaining_quantitiy


class Trade:
    trade_log = {}

    def __init__(self, trade_id, trade_price, trade_type, trade_quantity):
        self.trade_id = trade_id
        self.trade_price = trade_price
        self.trade_type = trade_type
        self.trade_quantity = trade_quantity

        Trade.trade_log[trade_id] = {
            "price": trade_price,
            "quantity": trade_quantity,
            "type": trade_type,
        }

    @classmethod
    def get_trade_log(cls):
        return cls.trade_log

    def get_trade_info(self):
        return f"Trade ID: {self.trade_id}\t Trade price: {self.trade_price}\t Trade Quantity: {self.trade_quantity}\t Total: {self.trade_quantity * self.trade_price}"


orderbook = OrderBook()

# Test with added side once FOK orders are implemented
# def main():
#     new_order = Order(100, 1000, "sell")
#     new_order2 = Order(100, 500, "buy")
#     orderbook.fill_order(new_order)
#     orderbook.fill_order(new_order2)
#     return orderbook.asks, orderbook.bids


# print(main())
