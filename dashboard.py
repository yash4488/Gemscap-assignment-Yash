import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import statsmodels.api as sm

st.set_page_config(page_title="Quant Dashboard", layout="wide")
st.title("📊 Quant Real-Time Analytics Dashboard")

# ---------------- SIDEBAR ----------------
symbols = ["BTCUSDT", "ETHUSDT"]

symbol_a = st.sidebar.selectbox("Symbol A", symbols, key="a")
symbol_b = st.sidebar.selectbox(
    "Symbol B",
    [s for s in symbols if s != symbol_a],
    key="b"
)

window = st.sidebar.slider("Rolling Window", 20, 200, 60, key="w")
z_thresh = st.sidebar.slider("Z Alert", 1.0, 3.0, 2.0, 0.1, key="z")

# ---------------- LOAD DATA ----------------
@st.cache_data(ttl=1)
def load(symbol):
    conn = sqlite3.connect("ticks.db")
    df = pd.read_sql(
        """
        SELECT timestamp, price
        FROM ticks
        WHERE symbol=?
        ORDER BY timestamp DESC
        LIMIT 1000
        """,
        conn,
        params=(symbol,)
    )
    conn.close()
    return df.sort_values("timestamp")

df_a = load(symbol_a)
df_b = load(symbol_b)

if len(df_a) < window or len(df_b) < window:
    st.warning("Waiting for live data...")
    st.stop()

df = pd.merge(df_a, df_b, on="timestamp", suffixes=("_a", "_b"))

# ---------------- ANALYTICS ----------------
y = df["price_a"]
x = sm.add_constant(df["price_b"])
model = sm.OLS(y, x).fit()
hedge = model.params[1]

df["spread"] = df["price_a"] - hedge * df["price_b"]
df["z"] = (df["spread"] - df["spread"].rolling(window).mean()) / df["spread"].rolling(window).std()
df["corr"] = df["price_a"].rolling(window).corr(df["price_b"])

latest_z = df["z"].iloc[-1]

if abs(latest_z) > z_thresh:
    st.error(f"🚨 Z-Score Alert: {latest_z:.2f}")

# ---------------- METRICS ----------------
c1, c2, c3 = st.columns(3)
c1.metric("Hedge Ratio", f"{hedge:.4f}")
c2.metric("Z-Score", f"{latest_z:.2f}")
c3.metric("Correlation", f"{df['corr'].iloc[-1]:.2f}")

# ---------------- CHARTS ----------------
price_fig = go.Figure()
price_fig.add_trace(go.Scatter(x=df["timestamp"], y=df["price_a"], name=symbol_a))
price_fig.add_trace(go.Scatter(x=df["timestamp"], y=df["price_b"], name=symbol_b))
price_fig.update_layout(title="Prices")

spread_fig = go.Figure()
spread_fig.add_trace(go.Scatter(x=df["timestamp"], y=df["spread"], name="Spread"))
spread_fig.add_trace(go.Scatter(x=df["timestamp"], y=df["z"], name="Z-Score", yaxis="y2"))
spread_fig.update_layout(
    title="Spread & Z-Score",
    yaxis2=dict(overlaying="y", side="right")
)

st.plotly_chart(price_fig, use_container_width=True)
st.plotly_chart(spread_fig, use_container_width=True)

st.download_button(
    "⬇ Download CSV",
    df.to_csv(index=False),
    "analytics.csv",
    "text/csv"
)
