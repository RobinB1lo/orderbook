"""
Allows running the server with:
    python -m orderbook
"""
import uvicorn


def main():
    uvicorn.run("orderbook.app:app", host="0.0.0.0", port=3000, reload=True, app_dir="src")


if __name__ == "__main__":
    main()
