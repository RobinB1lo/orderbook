import yfinance as yf


def get_current_price(symbol: str) -> float:
    ticker = yf.Ticker(symbol)

    # First attempt: fast_info.last_price — a single lightweight request that
    # returns the most recent traded price regardless of market hours.
    try:
        price = ticker.fast_info.last_price
        if price:
            return float(price)
    except Exception as e:
        print(f"fast_info failed for {symbol}: {e}")

    # Fallback: pull the last 5 days of daily closes, which always has data
    # even on weekends (it just returns the most recent trading day).
    try:
        data = ticker.history(period="5d", interval="1d")
        if not data.empty:
            return float(data["Close"].iloc[-1])
    except Exception as e:
        print(f"history fallback failed for {symbol}: {e}")

    print(f"All price sources failed for {symbol}. Using placeholder price.")
    return 100.0
