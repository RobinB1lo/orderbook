import yfinance as yf


def get_current_price(symbol: str) -> float:
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
