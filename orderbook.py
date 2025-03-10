import bisect
from side import Side
import yfinance as yf # for future featurs 
import datetime as dt #for future features
import time #for future features
import csv #for future features

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
        while remaining_quantity > 0 and self.ask_prices:
            best_ask_price = self.ask_prices[0]
            if best_ask_price > order.get_order_price():
                break
            ask_orders = []
            for ask in self.asks:
                if ask == best_ask_price:
                    ask_orders.append(ask)
            while ask_orders and remaining_quantity > 0:
                curr_ask = ask_orders[0]
                trade_quantitiy = min(curr_ask.remaining_quantitiy, remaining_quantity)
                self.execute_trade(best_ask_price, trade_quantitiy)
                curr_ask.remaining_quantitiy -= trade_quantitiy
                remaining_quantity -= trade_quantitiy
                if curr_ask.remaining_quantitiy == 0:
                    ask_orders.pop(0)
                    self.orders.pop(curr_ask.orderID)
                    if not ask_orders:
                        self.ask_prices.pop(0)
                        del self.asks[best_ask_price]
        if remaining_quantity > 0:
            order.remaining_quantitiy = remaining_quantity
            self.add_bid(order)
        return True

    def process_sell_order(self, order):
        remaining_quantity = order.remaining_quantitiy
        while remaining_quantity > 0 and self.bid_prices:
            best_bid_price = self.bid_prices[0]
            if best_bid_price < order.get_order_price():
                break
            bid_orders = []
            for bid in self.bids:
                if bid == best_bid_price:
                    bid_orders.append(bid)
            while bid_orders and remaining_quantity < 0:
                curr_bid = bid_orders[0]
                trade_quantity = min(curr_bid.remaining_quantity, remaining_quantity)
                self.execute_trade(best_bid_price, trade_quantity)
                curr_bid.remaining_quantity -= trade_quantity
                remaining_quantity -= trade_quantity
                if curr_bid.remaining_quantity == 0:
                    bid_orders.pop(0)
                    self.orders.pop(curr_bid.orderID)
                    if not bid_orders:
                        self.bid_prices.pop(0)
                        del self.bids[best_bid_price]
        if remaining_quantity > 0:
            order.remaining_quantitiy = remaining_quantity
            self.add_ask(order)
        return True

    def execute_trade(self, price, quantitiy):
        trade_id = len(Trade.trade_log) + 1
        Trade(trade_id, price, quantitiy)

    def add_bid(self, order):
        price = order.get_order_price()
        temp = []
        if price not in self.bids:
            for p in self.bid_prices:
                temp.append(-p)
            index = bisect.bisect_left(temp, -price)
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

    def __init__(self, orderprice, orderquantity, side):
        if side not in (Side.SELL, Side.BUY):
            raise ValueError("Side must be 0 (sell) or 1 (buy)")
        self.orderID = Order._next_orderId_
        self.initialquantitiy = orderquantity
        self.remaining_quantitiy = orderquantity
        self.order_price = orderprice
        self.order_side = side
        Order._next_orderId_ += 1

    def get_order_price(self):
        return self.order_price

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

    def __init__(self, trade_id, bid, ask, trade_price, trade_quantity):
        self.trade_id = trade_id
        self.trade_price = trade_price
        self.trade_quantity = trade_quantity

        Trade.trade_log[trade_id] = {"price": trade_price, "quantity": trade_quantity}

    @classmethod
    def get_trade_log(cls):
        return cls.trade_log

    def get_trade_info(self):
        return f"Trade ID: {self.trade_id}\t Trade price: {self.trade_price}\t Trade Quantity: {self.trade_quantity}\t Total: {self.trade_quantity * self.trade_price}"

orderbook = OrderBook()

def main():
    new_order = Order(100, 1000, "sell")
    new_order2 = Order(100, 500, "buy")
    orderbook.fill_order(new_order)
    orderbook.fill_order(new_order2)
    return orderbook.asks, orderbook.bids
    
print(main())