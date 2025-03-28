from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import bisect
from enum import StrEnum
import yfinance as yf

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="templates")


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class Type(StrEnum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    FOK = "FOK"


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

                self.execute_trade(
                    curr_ask.order_price, trade_quantity, order.order_type
                )

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

                self.execute_trade(
                    curr_bid.order_price, trade_quantity, order.order_type
                )

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

    def execute_trade(self, price, quantity, order_type):
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
        return f"Trade ID: {self.trade_id}\t Trade price: {self.trade_price}\t Trade Quantity: {self.trade_quantity}\t Total: {self.trade_quantity * self.trade_price}"


order_books = {}


def get_current_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1m")
        if not data.empty:
            return float(data["Close"].iloc[-1])
        print(f"No data for {symbol}. Using placeholder price.")
        return 100.0
    except Exception as e:
        print(f"Price error for {symbol}: {str(e)}")
        return 100.0


class OrderRequest(BaseModel):
    symbol: str
    side: Side
    type: Type
    price: float
    quantity: int


@app.get("/", response_class=HTMLResponse)
async def trading_interface(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/order")
async def place_order(order: OrderRequest):
    print(f"Received order: {order}")

    if order.symbol not in order_books:
        order_books[order.symbol] = OrderBook()

    try:
        side = Side.BUY if order.side == "BUY" else Side.SELL
        order_type = {"LIMIT": Type.LIMIT, "MARKET": Type.MARKET, "FOK": Type.FOK}[
            order.type
        ]

        order_obj = Order(
            orderprice=order.price,
            orderquantity=order.quantity,
            type=order_type,
            side=side,
        )

        ob = order_books[order.symbol]
        success = ob.fill_order(order_obj)

        if not success:
            raise HTTPException(400, detail="Order could not be filled")

        return {"status": "success", "order_id": order_obj.orderID}

    except Exception as e:
        print(f"Order failed: {str(e)}")
        raise HTTPException(400, detail=str(e))


@app.get("/api/orderbook/{symbol}")
async def get_orderbook(symbol: str):
    if symbol not in order_books:
        order_books[symbol] = OrderBook()

    ob = order_books[symbol]
    current_price = get_current_price(symbol)

    return {
        "price": current_price if current_price else 100.0,  # Fallback price
        "bids": {
            price: [o.remaining_quantity for o in orders]
            for price, orders in ob.bids.items()
        },
        "asks": {
            price: [o.remaining_quantity for o in orders]
            for price, orders in ob.asks.items()
        },
    }


@app.get("/api/trades")
async def get_trades():
    return Trade.trade_log


@app.delete("/api/order/{order_id}")
async def cancel_order(order_id: int):
    for symbol, ob in order_books.items():
        if ob.cancel_order(order_id):
            return {"status": "cancelled"}
    raise HTTPException(404, detail="Order not found")
