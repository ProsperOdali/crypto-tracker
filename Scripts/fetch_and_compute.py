import requests
import sqlite3
import pandas as pd

url = r"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30"


def fetch_data_from_api(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()

def create_and_insert_data(json_data, filename: str):
    conn = sqlite3.connect(filename)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
                timestamp INTEGER PRIMARY KEY,
                price REAL,
                market_cap REAL,
                total_volume REAL);
    """)

    prices = json_data["prices"]
    market_caps = json_data["market_caps"]
    total_volumes = json_data["total_volumes"]

    for i in range(len(prices)):
        timestamp = int(prices[i][0])
        price = float(prices[i][1])
        market_cap = float(market_caps[i][1])
        total_volume = float(total_volumes[i][1])

        cur.execute("""
        INSERT OR REPLACE INTO market_data (timestamp, price, market_cap, total_volume)
        VALUES (?, ?, ?, ?)            
        """, (timestamp, price, market_cap, total_volume))

    conn.commit()
    conn.close()
    print("DB file successfully created and data successfully inserted!")

def compute_metrics(filename: str):
    conn = sqlite3.connect(filename)
    df = pd.read_sql("SELECT * FROM market_data ORDER BY timestamp", conn)
    conn.close()

    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['returns'] = df['price'].pct_change()
    df['volatility'] = df['returns'].rolling(window=7).std()
    df['ma_7'] = df['price'].rolling(window=7).mean()

    return df



data = fetch_data_from_api(url)
create_and_insert_data(data, "crypto.db")
latest = compute_metrics("crypto.db").dropna()
latest.to_csv("data/bitcoin_market_data.csv", index=False)
