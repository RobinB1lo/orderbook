from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .engine import OrderBook
from .market_data import get_current_price
from .models import Order, Side, Trade, Type
from .schemas import OrderRequest

router = APIRouter()
templates = Jinja2Templates(directory="templates")

order_books: dict[str, OrderBook] = {}


@router.get("/", response_class=HTMLResponse)
async def trading_interface(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/api/order")
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

    except HTTPException:
        raise
    except Exception as e:
        print(f"Order failed: {str(e)}")
        raise HTTPException(400, detail=str(e))


@router.get("/api/orderbook/{symbol}")
async def get_orderbook(symbol: str):
    if symbol not in order_books:
        order_books[symbol] = OrderBook()

    ob = order_books[symbol]
    current_price = get_current_price(symbol)

    return {
        "price": current_price if current_price else 100.0,
        "bids": {
            price: [o.remaining_quantity for o in orders]
            for price, orders in ob.bids.items()
        },
        "asks": {
            price: [o.remaining_quantity for o in orders]
            for price, orders in ob.asks.items()
        },
    }


@router.get("/api/trades")
async def get_trades():
    return Trade.trade_log


@router.delete("/api/order/{order_id}")
async def cancel_order(order_id: int):
    for symbol, ob in order_books.items():
        if ob.cancel_order(order_id):
            return {"status": "cancelled"}
    raise HTTPException(404, detail="Order not found")
