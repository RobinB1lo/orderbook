from enum import StrEnum


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class Type(StrEnum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    FOK = "FOK"


class Order:
    _next_orderId_ = 0

    def __init__(self, orderprice, orderquantity, type, side):
        if side not in (Side.SELL, Side.BUY):
            raise ValueError("Side must be SELL or BUY")
        if type not in (Type.FOK, Type.LIMIT, Type.MARKET):
            raise ValueError("Type must be LIMIT, MARKET, or FOK")
        self.orderID = Order._next_orderId_
        self.initial_quantity = orderquantity
        self.remaining_quantity = orderquantity
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

    def get_initial_quantity(self):
        return self.initial_quantity

    def get_remaining_quantity(self):
        return self.remaining_quantity

    def get_filled_quantity(self):
        return self.initial_quantity - self.remaining_quantity


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
        return (
            f"Trade ID: {self.trade_id}\t"
            f" Trade price: {self.trade_price}\t"
            f" Trade Quantity: {self.trade_quantity}\t"
            f" Total: {self.trade_quantity * self.trade_price}"
        )
