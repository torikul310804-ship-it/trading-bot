import streamlit as st
import datetime
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from data_feed import TICKER_MAP, fetch_market_data
from signal_engine import QuantitativeSignalEngine

st.set_page_config(
    page_title="QuantVision 1M/5M Real-Time Engine",
    page_icon="⚡",
    layout="wide"
)

# ১০ সেকেন্ড (১০,০০০ মিলি-সেকেন্ড) পর পর পেজ অটো-রিফ্রেশ হবে
count = st_autorefresh(interval=10000, limit=10000, key="bot_autorefresh")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e222d; padding: 15px; border-radius: 10px; }
    .price-box { background-color: #1a1e29; border: 2px solid #00b4d8; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

col_title, col_clock = st.columns([3, 1])
with col_title:
    st.title("⚡ QuantVision Auto-Refreshing Signal Engine")
    st.caption("Auto-refreshes every 10 seconds | 1M & 5M Confluence Analysis")

with col_clock:
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S UTC")
    st.metric(label="Live UTC Clock", value=utc_now)

st.divider()

col_select, col_tf = st.columns([2, 1])
with col_select:
    selected_pair = st.selectbox(
        "Select Market Pair:",
        options=list(TICKER_MAP.keys()),
        index=0
    )

with col_tf:
    timeframe = st.radio("Chart Timeframe", ["1-Minute", "5-Minute"], horizontal=True)

# ডাটা ফেচিং
df_1m, df_5m = fetch_market_data(selected_pair)
engine = QuantitativeSignalEngine(df_1m, df_5m)
result = engine.analyze_signal()

df_target = engine.df_1m if timeframe == "1-Minute" else df_5m
current_price = df_target["Close"].iloc[-1]
prev_price = df_target["Close"].iloc[-2]
price_diff = current_price - prev_price

# বর্তমান প্রাইস দেখানো
col_price, col_signal = st.columns([1, 2])

with col_price:
    st.markdown(f"""
        <div class="price-box">
            <h4 style="color: #8d99ae; margin:0;">LIVE PRICE ({selected_pair})</h4>
            <h1 style="color: {'#2dc653' if price_diff >= 0 else '#e63946'}; margin:5px 0;">{current_price:.5f}</h1>
            <p style="color: {'#2dc653' if price_diff >= 0 else '#e63946'}; margin:0;">
                {'▲' if price_diff >= 0 else '▼'} {price_diff:+.5f}
            </p>
        </div>
    """, unsafe_allow_html=True)

with col_signal:
    action = result["action"]
    card_bg = "#1b4332" if "BUY" in action else ("#4c1d1d" if "SELL" in action else "#2b2d42")
    border_color = "#2dc653" if "BUY" in action else ("#e63946" if "SELL" in action else "#8d99ae")

    st.markdown(f"""
        <div style="background-color: {card_bg}; border: 2px solid {border_color}; padding: 15px; border-radius: 10px;">
            <h3 style="margin:0; color: white;">Signal: {result['action']}</h3>
            <h5 style="color: #edf2f4; margin-top:5px;">Confidence: {result['confidence']}</h5>
            <p style="color: #8d99ae; margin:0;">Status: <b>{result['status']}</b></p>
        </div>
    """, unsafe_allow_html=True)

st.write("")
col_reasons, col_risk = st.columns([2, 1])

with col_reasons:
    st.markdown("### 📊 Strategy Breakdown")
    for reason in result["reasons"]:
        st.markdown(f"- {reason}")

with col_risk:
    st.markdown("### 🛡️ Risk Rule")
    st.info(result["risk_advice"])

st.divider()

# ক্যান্ডেলস্টিক চার্ট
st.subheader(f"Price Action Chart ({timeframe}) — {selected_pair}")

fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df_target.index,
    open=df_target['Open'],
    high=df_target['High'],
    low=df_target['Low'],
    close=df_target['Close'],
    name="OHLC"
))

if 'EMA_20' in df_target.columns:
    fig.add_trace(go.Scatter(x=df_target.index, y=df_target['EMA_20'], line=dict(color='#00b4d8', width=1.5), name="EMA 20"))
if 'EMA_50' in df_target.columns:
    fig.add_trace(go.Scatter(x=df_target.index, y=df_target['EMA_50'], line=dict(color='#ffb703', width=1.5), name="EMA 50"))

fig.update_layout(
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    height=450,
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig, use_container_width=True)
    
