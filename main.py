if __name__ == "__main__":
    import uvicorn
    uvicorn.run("orderbook.app:app", host="0.0.0.0", port=3000, reload=True, app_dir="src")