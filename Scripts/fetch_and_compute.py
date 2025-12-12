import requests
import pandas as pd

API_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30"

def fetch_data():
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    return r.json()


def build_dataframe(data):
    prices = data["prices"]
    market_caps = data["market_caps"]
    total_volumes = data["total_volumes"]

    df = pd.DataFrame({
        "timestamp": [p[0] for p in prices],
        "price":     [p[1] for p in prices],
        "market_cap": [m[1] for m in market_caps],
        "total_volume": [v[1] for v in total_volumes],
    })

    # Convert to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    # Compute metrics
    df["returns"] = df["price"].pct_change() * 100        # percent
    df["volatility"] = df["returns"].rolling(7).std()     # already % because returns is %
    df["ma_7"] = df["price"].rolling(7).mean()
    df["ma_21"] = df["price"].rolling(21).mean()

    # Drop rows with missing values (beginning of the dataset)
    df = df.dropna().reset_index(drop=True)

    return df


def save_csv(df):
    df.to_csv("data/bitcoin_market_data.csv", index=False)
    print("CSV saved → data/bitcoin_market_data.csv")
    print(f"Rows: {len(df)}")


if __name__ == "__main__":
    print("Fetching BTC market data…")
    raw = fetch_data()
    df = build_dataframe(raw)
    save_csv(df)
