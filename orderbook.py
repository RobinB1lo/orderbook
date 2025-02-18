class OrderBook:
    def __init__(self):
        self.orders = {}

    def fillOrder(self, ord):
        return 
    
    def cancelOrder(self, ordID):
        return 
    
    def bids(self):
        return 
    
    def asks(self):
        return 


class Order:
    _next_orderId_ = 0

    def __init__(self, orderquantity, side): 
        self.orderID = Order._next_orderId_
        self.initialquantitiy = self.remainingquantitiy = orderquantity
        Order._next_orderId_ += 1
        self.orderside = side
    
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
    def __init__(self):
        return 
    
    def tradeInfo(self):
        return 
    
class MatchingEngine:
    def __init__(self):
        return
