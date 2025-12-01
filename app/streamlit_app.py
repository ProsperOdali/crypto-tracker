import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Config
st.set_page_config(page_title="BTC Live Dashboard", page_icon="₿", layout="wide")
st.title("₿ Bitcoin Live Dashboard")
st.caption("All metrics calculated & updated every hour • Powered by GitHub Actions")

# Raw CSV URL — change only if you rename the file or folder
CSV_URL = "https://github.com/ProsperOdali/crypto-tracker/blob/main/data/bitcoin_market_data.csv"
@st.cache_data(ttl=1800)  # Refresh max every 30 mins
def load_data():
    df = pd.read_csv(CSV_URL)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date_time'] = pd.to_datetime(df['date_time'])
    return df.sort_values('timestamp').reset_index(drop=True)

df = load_data()
latest = df.iloc[-1]

# ==================== SIDEBAR ====================
st.sidebar.header("₿ Current Stats")
st.sidebar.metric("Price", f"${latest['price']:,.2f}")
st.sidebar.metric("Market Cap", f"${latest['market_cap']:,.0f}")
st.sidebar.metric("24h Volume", f"${latest['total_volume']:,.0f}")
st.sidebar.metric("7-Day Volatility", f"{latest['volatility']:.2f}%")
st.sidebar.metric("Latest Return", f"{latest['returns']:+.4f}%")

st.sidebar.write(f"**Last updated:** {latest['timestamp'].strftime('%Y-%m-%d %H:%M UTC')}")

# ==================== TOP METRICS ====================
col1, col2, col3, col4 = st.columns(4)
col1.metric("BTC Price", f"${latest['price']:,.2f}")
col2.metric("24h Change", f"{(df['price'].pct_change().iloc[-1]*100):+.2f}%")
col3.metric("7-Day MA", f"${latest['ma_7']:,.0f}")
col4.metric("21-Day MA", f"${latest['ma_21']:,.0f}")

# ==================== PRICE CHART ====================
st.subheader("Price & Moving Averages")
fig_price = go.Figure()

fig_price.add_trace(go.Scatter(x=df['timestamp'], y=df['price'], name="Price", line=dict(color="#F7931A", width=3)))
fig_price.add_trace(go.Scatter(x=df['timestamp'], y=df['ma_7'], name="MA 7", line=dict(color="#FF6B6B")))
fig_price.add_trace(go.Scatter(x=df['timestamp'], y=df['ma_21'], name="MA 21", line=dict(color="#4ECDC4")))

fig_price.update_layout(height=500, hovermode="x unified", template="plotly_dark")
st.plotly_chart(fig_price, use_container_width=True)

# ==================== MARKET CAP & VOLUME ====================
st.subheader("Market Cap & Volume")
fig_cap_vol = go.Figure()
fig_cap_vol.add_trace(go.Bar(x=df['timestamp'], y=df['market_cap']/1e9, name="Market Cap (B)", yaxis="y"))
fig_cap_vol.add_trace(go.Scatter(x=df['timestamp'], y=df['total_volume']/1e9, name="Volume (B)", yaxis="y2", line=dict(color="#00FF88")))

fig_cap_vol.update_layout(
    barmode='overlay',
    height=400,
    yaxis=dict(title="Market Cap (Billions USD)"),
    yaxis2=dict(title="Volume (Billions USD)", overlaying="y", side="right"),
    template="plotly_dark"
)
st.plotly_chart(fig_cap_vol, use_container_width=True)

# ==================== VOLATILITY & RETURNS ====================
col1, col2 = st.columns(2)

with col1:
    st.subheader("7-Day Rolling Volatility")
    fig_vol = px.area(df, x='timestamp', y='volatility', color_discrete_sequence=["#FF6B6B"])
    fig_vol.update_layout(height=350, template="plotly_dark")
    st.plotly_chart(fig_vol, use_container_width=True)

with col2:
    st.subheader("Hourly Returns")
    fig_ret = px.bar(df, x='timestamp', y='returns', color='returns',
                     color_continuous_scale=["red", "gray", "green"])
    fig_ret.update_layout(height=350, template="plotly_dark", showlegend=False)
    st.plotly_chart(fig_ret, use_container_width=True)

# ==================== RAW DATA (optional) ====================
with st.expander("Show Raw Data Table (latest 100 rows)"):
    display_df = df.tail(100).copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(display_df.style.format({
        'price': '${:,.2f}',
        'market_cap': '${:,.0f}',
        'total_volume': '${:,.0f}',
        'returns': '{:+.4f}%',
        'volatility': '{:.2f}%',
        'ma_7': '${:,.0f}',
        'ma_21': '${:,.0f}'
    }))

# Footer
st.markdown("---")
st.markdown("Built with ❤️ by ProsperOdal • Hosted free on Streamlit • Data auto-updated hourly")
