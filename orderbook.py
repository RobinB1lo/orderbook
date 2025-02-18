from collections import defaultdict

class OrderBook:
    def __init__(self):
        self.asks = {}
        self.bids = {}

    def fillOrder(self, ord):
        return 
    
    def cancelOrder(self, ordID):
        return 
    
    def addBid():
        
        return 
    
    def addAsk():
        
        return 


class Order:
    _next_orderId_ = 0

    def __init__(self, orderquantity, side): 
        self.orderID = Order._next_orderId_
        self.initialquantitiy = self.remainingquantitiy = orderquantity
        self.orderside = side
        Order._next_orderId_ += 1
    
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
    def __init__(self):
        return
    
=
