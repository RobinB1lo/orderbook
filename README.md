# RobinBook — Interactive Order Book

A web-based limit order book simulation built with FastAPI and Python. Place limit, market, and fill-or-kill orders against live market prices fetched from Yahoo Finance.

## How to Run

**Prerequisites:** Python 3.12+

```bash
pip install fastapi uvicorn yfinance jinja2 python-multipart
python main.py
```

Then open `http://localhost:3000` in your browser.

## Project Structure

```
orderbook/
├── main.py               # Entry point — starts the uvicorn server
├── app/
│   └── orderbook.py      # FastAPI app, order book engine, data models
├── templates/
│   └── index.html        # Trading UI
└── static/
    └── trading.js        # Frontend logic (order placement, live updates)
```

## How the Application Works

The backend exposes three REST endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/order` | Place a new order |
| `GET` | `/api/orderbook/{symbol}` | Fetch current bids/asks + live price |
| `DELETE` | `/api/order/{order_id}` | Cancel a resting order |

The frontend polls `/api/orderbook` and `/api/trades` every 2 seconds to keep the display current. Supported symbols: **TSLA**, **AAPL**, **GOOG** — each gets its own independent order book instance. Live prices are pulled from Yahoo Finance via `yfinance`.

## How an Order Book Works

An order book is the core matching mechanism used by every financial exchange. It maintains two sorted lists of outstanding orders:

- **Bids** — buy orders, sorted highest price first (buyers willing to pay the most get priority)
- **Asks** — sell orders, sorted lowest price first (sellers asking the least get priority)

The difference between the best ask and best bid is called the **spread**.

### Order Types

**Limit Order**
A buy or sell order at a specific price or better. If it can't be immediately matched, it rests on the book until a counterparty arrives.
- A limit buy at $150 will only execute against asks priced ≤ $150.
- Unfilled remainder stays in the book.

**Market Order**
Executes immediately at whatever price is currently available. Walks through resting orders on the opposite side until filled or the book is exhausted.
- No price guarantee — in a thin market, execution price can be far from the last traded price (slippage).

**Fill-or-Kill (FOK)**
Must be filled in its entirety immediately, or it is cancelled. Before execution begins, the engine checks whether enough liquidity exists at acceptable prices. If not, the order is rejected outright — no partial fills, nothing rests on the book.

### Matching Algorithm

When an order arrives, the engine:

1. **Checks the opposite side** of the book for crossing prices (bid price ≥ best ask, or ask price ≤ best bid).
2. **Executes trades** at the resting order's price, consuming quantity from the front of the queue at each price level (price-time priority).
3. **Repeats** until the incoming order is filled, no more crossing prices exist, or (for FOK) the order fails.
4. **Rests the remainder** on the book (limit orders only) if not fully filled.

### Price-Time Priority

Orders at the same price level are filled in the order they were received — first in, first out. This rewards participants who post liquidity early.

### Example

```
Asks:  $152 x 100,  $151 x 50
Bids:  $150 x 200,  $149 x 75
```

A market buy order for 120 shares would:
1. Take all 50 shares at $151
2. Take 70 shares at $152
3. Fully fill — 120 shares matched across two price levels

### Trading Bots

We introduce trading bots which are meant to simulate the behaviour of various market participants in the financial markets. Thes bots can each be activated individually through the UI. 

We have the following bots so far:

1. The market maker 
    - The market maker's goal is quite literally to "make markets", providing liquidity to other market participants. Our bot will make markets and try to keep the bid-ask spread of the orderbook tight while hedging it's positions

2. Fundamental trader
    - The fundamental trader looks to profit from companie's stock prices being over or under valued, when a stock is under valued they enter into a long position, conversly when a stock is over valued they enter into a short position. We will program an intrinsic value for each stock for which the fundamental bot will base it's trades of of

3. Chartist/Trend trader
    - The Trend trader tries to make trades based off of the trend of the chart, a common strategy is moving averages which we will implement with out bot

4. High frequency trader
    - Ultra fast algorithms that react to orderbook changes rather than long term value. Our bot will be written in C++ to simulate the quickness of the HFT's

5. Institutional "Whales"
    - Large entities that move massive amounts of capital, sometimes clearing out the whole orderbook

6. Noise/Random liquidity takers
    - Random retail traders, which creates a base line for our orderbook making sure the environment stays dynamic
