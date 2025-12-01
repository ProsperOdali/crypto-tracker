import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Bitcoin Live Tracker", layout="wide")
st.title("Bitcoin Market Data – Live from GitHub")

# Direct raw URL to your CSV (this is the magic part)
CSV_URL = "https://raw.githubusercontent.com/ProsperOdal/crypto-tracker/main/data/bitcoin_market_data.csv"

@st.cache_data(ttl=3600)  # refresh max once per hour
def load_data():
    df = pd.read_csv(CSV_URL)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    elif 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# Show last update time
st.sidebar.success(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")

# Key metrics
latest = df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Price USD", f"${latest['price_usd']:,.2f}")
col2.metric("24h Change", f"{latest['percent_change_24h']:+.2f}%")
col3.metric("Market Cap", f"${latest['market_cap']:,.0f}")
col4.metric("24h Volume", f"${latest['volume_24h']:,.0f}")

# Price chart
st.subheader("Price Over Time")
fig = px.line(df, x=df.columns[0], y="price_usd", title="BTC/USD")
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# Full table (optional)
if st.checkbox("Show raw data table"):
    st.dataframe(df.tail(50))
