import streamlit as st
import datetime
import plotly.graph_objects as go
from data_feed import TICKER_MAP, fetch_market_data
from signal_engine import QuantitativeSignalEngine

st.set_page_config(
    page_title="QuantVision - 1M OTC/Forex Trading Bot",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e222d; padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

col_title, col_clock = st.columns([3, 1])
with col_title:
    st.title("⚡ QuantVision 1M Binary/Forex Signal Engine")
    st.caption("Quantitative Price Action & Microstructure Analysis")

with col_clock:
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S UTC")
    st.metric(label="Live UTC Clock", value=utc_now)

st.divider()

col_select, col_btn = st.columns([3, 1])
with col_select:
    selected_pair = st.selectbox(
        "Select Market Pair (Real & OTC):",
        options=list(TICKER_MAP.keys()),
        index=0
    )

with col_btn:
    st.write(" ")
    st.write(" ")
    analyze_clicked = st.button("🔍 ANALYZE 1M MARKET", type="primary", use_container_width=True)

if analyze_clicked:
    with st.spinner(f"Fetching real-time market depth for {selected_pair}..."):
        df_1m, df_5m = fetch_market_data(selected_pair)
        engine = QuantitativeSignalEngine(df_1m, df_5m)
        result = engine.analyze_signal()
        df_1m_computed = engine.df_1m

    st.subheader("Signal & Execution Analysis")

    action = result["action"]
    if "BUY" in action:
        card_bg = "#1b4332"
        border_color = "#2dc653"
    elif "SELL" in action:
        card_bg = "#4c1d1d"
        border_color = "#e63946"
    else:
        card_bg = "#2b2d42"
        border_color = "#8d99ae"

    st.markdown(f"""
        <div style="background-color: {card_bg}; border: 2px solid {border_color}; padding: 20px; border-radius: 10px;">
            <h2 style="margin:0; color: white;">Action: {result['action']}</h2>
            <h4 style="color: #edf2f4; margin-top:5px;">Confidence Score: {result['confidence']}</h4>
            <p style="color: #8d99ae; margin:0;">Status: <b>{result['status']}</b> | Timeframe: <b>{result['timeframe']}</b></p>
        </div>
    """, unsafe_allow_html=True)

    st.write("")

    col_reasons, col_risk = st.columns([2, 1])

    with col_reasons:
        st.markdown("### 📊 Strategy Confluence Breakdown")
        for reason in result["reasons"]:
            st.markdown(f"- {reason}")

    with col_risk:
        st.markdown("### 🛡️ Risk Management Rules")
        st.info(result["risk_advice"])

    st.divider()
    st.subheader(f"Price Action Chart (1-Minute) — {selected_pair}")

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df_1m_computed.index,
        open=df_1m_computed['Open'],
        high=df_1m_computed['High'],
        low=df_1m_computed['Low'],
        close=df_1m_computed['Close'],
        name="OHLC"
    ))

    if 'EMA_20' in df_1m_computed.columns:
        fig.add_trace(go.Scatter(x=df_1m_computed.index, y=df_1m_computed['EMA_20'], line=dict(color='#00b4d8', width=1.5), name="EMA 20"))
    if 'EMA_50' in df_1m_computed.columns:
        fig.add_trace(go.Scatter(x=df_1m_computed.index, y=df_1m_computed['EMA_50'], line=dict(color='#ffb703', width=1.5), name="EMA 50"))
    if 'BB_Upper' in df_1m_computed.columns:
        fig.add_trace(go.Scatter(x=df_1m_computed.index, y=df_1m_computed['BB_Upper'], line=dict(color='rgba(255,255,255,0.3)', dash='dash'), name="BB Upper"))
    if 'BB_Lower' in df_1m_computed.columns:
        fig.add_trace(go.Scatter(x=df_1m_computed.index, y=df_1m_computed['BB_Lower'], line=dict(color='rgba(255,255,255,0.3)', dash='dash'), name="BB Lower"))

    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=450,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)
    
