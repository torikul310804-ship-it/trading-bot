import streamlit as st
import datetime
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from data_feed import TICKER_MAP, fetch_market_data
from signal_engine import QuantitativeSignalEngine

st.set_page_config(
    page_title="QuantVision Pro - Real Market Signal Engine",
    page_icon="📈",
    layout="wide"
)

# প্রতি ৩ সেকেন্ড পর পর অটো-রিফ্রেশ
st_autorefresh(interval=3000, limit=100000, key="bot_autorefresh_pro")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .price-card { background-color: #161b22; border: 1px solid #30363d; padding: 18px; border-radius: 10px; text-align: center; }
    .signal-card-up { background-color: #064e3b; border: 2px solid #10b981; padding: 18px; border-radius: 10px; text-align: center; }
    .signal-card-down { background-color: #7f1d1d; border: 2px solid #ef4444; padding: 18px; border-radius: 10px; text-align: center; }
    .signal-card-neutral { background-color: #1f2937; border: 2px solid #4b5563; padding: 18px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# হেডার সেকশন
col_title, col_clock = st.columns([3, 1])
with col_title:
    st.title("📈 QuantVision Pro - Signal Engine")
    st.caption("Live Market Price & Signal Analytics for Real Forex Pairs")

with col_clock:
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S UTC")
    st.metric(label="Server UTC Clock", value=utc_now)

st.divider()

# পেয়ার ও টাইমফ্রেম সিলেক্টর
col_select, col_tf = st.columns([2, 1])
with col_select:
    selected_pair = st.selectbox(
        "Select Asset / Currency Pair:",
        options=list(TICKER_MAP.keys()),
        index=0
    )

with col_tf:
    timeframe = st.radio("Select Timeframe Mode", ["1-Minute", "5-Minute"], horizontal=True)

# ডাটা ফেচিং ও এনালাইসিস
df_1m, df_5m = fetch_market_data(selected_pair)
engine = QuantitativeSignalEngine(df_1m, df_5m)
result = engine.analyze_signal()

df_target = engine.df_1m if timeframe == "1-Minute" else df_5m

# বর্তমান লাইভ প্রাইস ক্যালকুলেশন
current_price = df_target["Close"].iloc[-1]
prev_price = df_target["Close"].iloc[-2]
price_diff = current_price - prev_price

# সিগন্যাল ডিরেকশন প্রসেস
action_raw = result.get("action", "").upper()
if "BUY" in action_raw or "CALL" in action_raw or "UP" in action_raw:
    sig_text = "CALL / UP 🟢"
    card_style = "signal-card-up"
    sub_desc = "Recommended Action: BUY / CALL Position"
elif "SELL" in action_raw or "PUT" in action_raw or "DOWN" in action_raw:
    sig_text = "PUT / DOWN 🔴"
    card_style = "signal-card-down"
    sub_desc = "Recommended Action: SELL / PUT Position"
else:
    sig_text = "WAIT ⏳"
    card_style = "signal-card-neutral"
    sub_desc = "Market Consolidating - Wait for Clear Trend"

# ডিসপ্লে লাইভ কার্ড
col_p, col_s = st.columns([1, 1.2])

with col_p:
    st.markdown(f"""
        <div class="price-card">
            <span style="color: #8b949e; font-size: 13px; font-weight: bold;">LIVE MARKET PRICE</span>
            <h1 style="color: {'#10b981' if price_diff >= 0 else '#ef4444'}; margin: 8px 0; font-size: 36px;">{current_price:.5f}</h1>
            <span style="color: {'#10b981' if price_diff >= 0 else '#ef4444'}; font-weight: bold;">
                {'▲' if price_diff >= 0 else '▼'} {price_diff:+.5f}
            </span>
        </div>
    """, unsafe_allow_html=True)

with col_s:
    st.markdown(f"""
        <div class="{card_style}">
            <span style="color: #d1d5db; font-size: 13px; font-weight: bold;">{timeframe.upper()} SIGNAL</span>
            <h1 style="color: white; margin: 4px 0; font-size: 38px;">{sig_text}</h1>
            <span style="color: #e5e7eb; font-size: 14px;">{sub_desc}</span>
        </div>
    """, unsafe_allow_html=True)

st.write("")

# নোটিশ বা ক্লায়েন্ট গাইড
if "OTC" in selected_pair:
    st.warning("⚠️ Notice: OTC markets are broker-generated. For 100% chart matching, trade Real Forex Pairs during market hours.")

# স্ট্র্যাটেজি এনালাইসিস ব্রেকডাউন
with st.expander("🔍 Confluence & Analysis Breakdown", expanded=True):
    for reason in result.get("reasons", []):
        st.markdown(f"• {reason}")

st.divider()

# ক্যান্ডেলস্টিক চার্ট সেকশন (শেষ ২৫টি ক্যান্ডেল)
st.subheader(f"📊 Price Chart ({timeframe}) — {selected_pair}")

df_chart = df_target.tail(25)

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df_chart.index,
    open=df_chart['Open'],
    high=df_chart['High'],
    low=df_chart['Low'],
    close=df_chart['Close'],
    increasing_line_color='#10b981',
    decreasing_line_color='#ef4444',
    name="Candles"
))

if 'EMA_20' in df_chart.columns:
    fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA_20'], line=dict(color='#00b4d8', width=1.5), name="EMA 20"))
if 'EMA_50' in df_chart.columns:
    fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA_50'], line=dict(color='#ffb703', width=1.5), name="EMA 50"))

fig.update_layout(
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    height=420,
    margin=dict(l=15, r=15, t=10, b=15),
    xaxis=dict(showgrid=True, gridcolor='#21262d'),
    yaxis=dict(showgrid=True, gridcolor='#21262d')
)

st.plotly_chart(fig, use_container_width=True)
