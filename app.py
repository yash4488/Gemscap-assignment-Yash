import asyncio
import json
import sqlite3
import websockets
import time

DB_FILE = "ticks.db"

# ------------------ DB SETUP ------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ticks (
            timestamp INTEGER,
            symbol TEXT,
            price REAL,
            qty REAL
        )
    """)
    conn.commit()
    conn.close()

# ------------------ BINANCE STREAM ------------------
async def stream():
    uri = "wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@trade"

    async with websockets.connect(uri) as ws:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        while True:
            msg = await ws.recv()
            data = json.loads(msg)["data"]

            ts = int(data["T"])
            symbol = data["s"]
            price = float(data["p"])
            qty = float(data["q"])

            c.execute(
                "INSERT INTO ticks VALUES (?, ?, ?, ?)",
                (ts, symbol, price, qty)
            )
            conn.commit()

            print(symbol, price)

# ------------------ MAIN ------------------
if __name__ == "__main__":
    init_db()
    asyncio.run(stream())
