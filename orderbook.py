import bisect

class OrderBook:
    def __init__(self):
        self.asks = {}
        self.bids = {}
        self.ask_prices = []
        self.bid_prices = []
        self.orders = {}

    def fill_order(self, order):
        if order.getorderSide().lower() == "buy":
            self.process_buy_order(order)
        elif order.getorderSide().lower() == "sell":
            self.process_sell_order(order)
        else:
            raise ValueError("Invalid order side")

    def process_buy_order(self, order):
        remaining_quantity = order.remainingquantitiy
        while remaining_quantity > 0 and self.ask_prices:
            best_ask_price = self.ask_prices[0]
            if best_ask_price > order.orderprice:
                break
            ask_orders = []
            for ask in self.asks:
                if ask.orderprice == best_ask_price:
                    ask_orders.append(ask)
            while ask_orders and remaining_quantity > 0:
                curr_ask = ask_orders[0]
                trade_quantitiy = min(curr_ask.remainingquantitiy, remaining_quantity)
                self.execute_trade(best_ask_price, trade_quantitiy)
                curr_ask.remainingquantitiy -= trade_quantitiy
                remaining_quantity -= trade_quantitiy
                if curr_ask.remainingquantitiy == 0:
                    ask_orders.pop(0)
                    self.orders.pop(curr_ask.orderID)
                    if not ask_orders:
                        self.ask_prices.pop(0)
                        del self.asks[best_ask_price]
        if remaining_quantity > 0:
            order.remainingquantitiy = remaining_quantity
            self.addbid(ord)
        return True

    def process_sell_order(self, order):
        remaining_quantity = order.remainingquantitiy
        while remaining_quantity > 0 and self.bid_prices:
            best_bid_price = self.bid_prices[0]
            if best_bid_price < order.orderprice:
                break
            bid_orders = []
            for bid in self.bids:
                if bid.orderprice == best_bid_price:
                    bid_orders.append(bid)
            while bid_orders and remaining_quantity < 0:
                curr_bid = bid_orders[0]
                trade_quantity = min(curr_bid.remainingquantity, remaining_quantity)
                self.execute_trade(best_bid_price, trade_quantity)
                curr_bid.remainingquantity -= trade_quantity
                remaining_quantity -= trade_quantity
                if curr_bid.remainingquantity == 0:
                    bid_orders.pop(0)
                    self.orders.pop(curr_bid.orderID)
                    if not bid_orders:
                        self.bid_prices.pop(0)
                        del self.bids[best_bid_price]
        if remaining_quantity > 0:
            order.remainingquantitiy = remaining_quantity
            self.addask(order)
        return True

    def execute_trade(self, price, quantitiy):
        trade_id = len(Trade.trade_log) + 1
        Trade(trade_id, price, quantitiy)

    def add_bid(self, order):
        price = order.orderprice
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
        price = order.orderprice
        if price not in self.asks:
            index = bisect.bisect_left(self.ask_prices, price)
            self.ask_prices.insert(index, price)
            self.bids[price] = []
        self.asks[price].append(order)
        self.orders[order.orderID] = (price, "ask")

    def cancel_order(self, orderID):
        if orderID not in self.orders:
            return False
        price, side = self.orders[orderID]
        del self.orders[orderID]
        if side == 'bid':
            for i in range(len(self.bids[price])):
                if self.bids[price][i] == price:
                    self.bids[price].pop(i)
        elif side == 'ask':
            for i in range(len(self.asks[price])):
                if self.asks[price][i] == price:
                    self.asks[price].pop(i)
        for i in range(len(self.bid_prices[price])):
                if self.bid_prices[i] == price:
                    self.bid_prices[price].pop(i)
        for i in range(len(self.ask_prices[price])):
                if self.ask_prices[i] == price:
                    self.ask_prices[price].pop(i)
        return True 
    
class Order:
    _next_orderId_ = 0

    def __init__(self, orderprice, orderquantity, side):
        self.orderID = Order._next_orderId_
        self.initialquantitiy = self.remainingquantitiy = orderquantity
        self.orderprice = orderprice
        self.orderside = side
        Order._next_orderId_ += 1

    def get_order_price(self):
        return self.orderprice

    def get_order_side(self):
        return self.orderside

    def get_order_id(self):
        return self.orderID

    def get_initial_quantitiy(self):
        return self.initialquantitiy

    def get_remaining_quantitiy(self):
        return self.remainingquantitiy

    def get_filled_quantity(self):
        return self.initialquantitiy - self.remainingquantitiy


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

#Will be the user interface, will start off as a command line app
#Have to add feature so that th euser can't cancel other people's orders 
def main():
    return 