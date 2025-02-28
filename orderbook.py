import bisect

class OrderBook:
    def __init__(self):
        self.asks = {}
        self.bids = {}
        self.ask_prices = {}
        self.bid_prices = {}
        self.orders = {}

    def fillOrder(self, ord):
        if ord.getorderSide().lower() == 'buy':
            self.process_buy_order(ord)
        elif ord.getorderSide().lower() == 'sell':
            self.process_sell_order(ord)
        else:
            raise ValueError('Invalid order side')
    
    def process_buy_order(ord):
        rem_quantity = ord.remainingquantitiy
        while rem_quantity > 0 and self.ask_prices:
            best_ask_price = self.ask_prices[0]
            if best_ask_price > ord.orderprice:
                break
            ask_orders = []
            for ask in self.asks:
                if ask.orderprice == best_ask_price:
                    ask_orders.append(ask)
            while ask_orders and rem_quantity > 0:
                curr_ask = ask_orders[0]
                trade_quantitiy = min(curr_ask.remainingquantitiy, rem_quantity)
                self.execute_trade(curr_ask, ord, best_ask_price, trade_quantitiy)
                curr_ask.remainingquantitiy -= trade_quantitiy
                rem_quantity -= trade_quantitiy
                if curr_ask.remainingquantitiy == 0:
                    ask_orders.pop(0)
                    self.orders.pop(curr_ask.orderID)
                    if not ask_orders:
                        self.ask_prices.pop(0)
                        del self.asks[best_ask_price]
        if rem_quantity > 0:
            ord.remainingquantitiy = rem_quantity
            self.addbid(ord)
        return True
    
    def process_sell_order(ord):
        rem_quantity = ord.remainingquantitiy
        while rem_quantity > 0 and self.bid_prices:
            best_bid_price = self.bid_prices[0]
            if best_bid_price < ord.orderprice:
                break
            bid_orders = []
            for bid in self.bids:
                if bid.orderprice == best_bid_price:
                    bid_orders.append(bid)
            while bid_orders and rem_quantity < 0:
                curr_bid = bid_orders[0]
                trade_quantity = min(curr_bid.remainingquantity, rem_quantity)
                self.execute_trade(ord, curr_bid, best_bid_price, trade_quantity)
                curr_bid.remainingquantity -= trade_quantity
                rem_quantity -= trade_quantity
                if curr_bid.remainingquantity == 0:
                    bid_orders.pop(0)
                    self.orders.pop(curr_bid.orderID)
                    if not bid_orders:
                        self.bid_prices.pop(0)
                        del self.bids[best_bid_price]
        if rem_quantity > 0:
            ord.remainingquantitiy = rem_quantity
            self.addask(ord)
        return True
    
    def execute_trade(self, sell_ord, buy_ord, price, quantitiy):
        ``
    
    def cancel_order(self, ordID):
        return 
    
    def addbid(ord):
        self.bid[ord.ordID] = ord.orderprice, ord.remainingquantity
    
    def addask(ord):
        self.ask[ord.orderID] = ord.orderprice, ord.remainingquantity
    
class Order:
    _next_orderId_ = 0

    def __init__(self, orderprice, orderquantity, side): 
        self.orderID = Order._next_orderId_
        self.initialquantitiy = self.remainingquantitiy = orderquantity
        self.orderprice = orderprice
        self.orderside = side
        Order._next_orderId_ += 1
    
    def getorderPrice(self):
        return self.orderprice
    
    def getorderSide(self):
        return self.orderside

    def getorderId(self):
        return self.orderID

    def getinitialquantitiy(self):
        return self.initialquantitiy

    def getremainingquantitiy(self):
        return self.remainingquantitiy
    
    def getfilledquantity(self):
        return (self.initialquantitiy - self.remainingquantitiy)
    

class Trade:

    trade_log = {}

    def __init__(self, trade_id, trade_price, trade_quantity):
        self.trade_id = trade_id
        self.trade_price = trade_price
        self.trade_quantity = trade_quantity
        
        Trade.trade_log[trade_id] = {
            'price' : trade_price,
            'quantity' : trade_quantity
        }
    
    @classmethod
    def getTradelog(cls):
        return cls.trade_log

    def getTradeinfo(self):
        return f"Trade ID: {self.trade_id}\t Trade price: {self.trade_price}\t Trade Quantity: {self.trade_quantity}\t Total: {self.trade_quantity * self.trade_price}"
    
class MatchingEngine:
    def __init__(self, asks, bids):
        self.asks = asks
        self.bids = bids 

    
    def matchorder(self, order, orderbook):
        for order in orderbook:
            orderbook[order]
        # the sorting might be a problem, right now the key is the ID of the order but do we want to make it the price, either way we will have to look through the while dict
        # maybe whe ninseerting in the bid and asks list we can order them in terms of price then time in a rolling manner, 
        # because the matching engine is used to see if an order can be matched right away and if it can't then it goes in the bids or asks dict and waits to be matched, if we can somehow place
        # them in the correct order it would work well we will just have to check evey price value int he dicts which is o(n) at worst 
        return