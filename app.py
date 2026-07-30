import os
import time
import random
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. GLOBAL PAGE CONFIG & CYBERPUNK STYLING
# ==========================================
st.set_page_config(
    page_title="QUANTX GLOBAL | AI HFT & Binary Options Exchange",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Live Market Auto-Refresh (Every 20 Seconds)
st_autorefresh(interval=20000, key="global_exchange_refresh")

# Institutional Cyberpunk Glassmorphism UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');

    :root {
        --bg-dark: #07090e;
        --card-bg: rgba(16, 22, 34, 0.85);
        --accent-green: #10b981;
        --accent-red: #f43f5e;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-yellow: #f59e0b;
        --border-glass: rgba(255, 255, 255, 0.08);
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
    }

    body, .stApp {
        background-color: var(--bg-dark);
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: var(--text-primary);
    }

    header, footer { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }

    /* Custom Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.9);
        padding: 8px;
        border-radius: 16px;
        border: 1px solid var(--border-glass);
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 12px;
        color: var(--text-secondary);
        font-family: 'Orbitron', sans-serif;
        font-size: 12px;
        font-weight: 600;
        background-color: transparent;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(16, 185, 129, 0.25)) !important;
        color: #ffffff !important;
        border: 1px solid rgba(59, 130, 246, 0.5) !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
    }

    /* Glass Cards */
    .glass-card {
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    }

    /* Typography & Utilities */
    .font-orbitron { font-family: 'Orbitron', sans-serif; }
    .text-green { color: var(--accent-green); text-shadow: 0 0 10px rgba(16, 185, 129, 0.4); }
    .text-red { color: var(--accent-red); text-shadow: 0 0 10px rgba(244, 63, 94, 0.4); }
    .text-blue { color: var(--accent-blue); text-shadow: 0 0 10px rgba(59, 130, 246, 0.4); }
    .text-purple { color: var(--accent-purple); text-shadow: 0 0 10px rgba(139, 92, 246, 0.4); }

    /* Action Buttons */
    .stButton > button {
        border-radius: 12px;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        transition: all 0.2s ease;
        border: none;
    }

    .btn-up > button {
        background: linear-gradient(135deg, #059669, #10b981) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }

    .btn-down > button {
        background: linear-gradient(135deg, #e11d48, #f43f5e) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(244, 63, 94, 0.4);
    }

    .btn-odd > button {
        background: linear-gradient(135deg, #7c3aed, #8b5cf6) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
    }

    .btn-even > button {
        background: linear-gradient(135deg, #d97706, #f59e0b) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
    }

    .badge-kyc {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 11px;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }

    .badge-pending {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 11px;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE MANAGEMENT & AUTH
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = {
        "username": "TraderGlobal",
        "email": "trader@quantx.io",
        "balance": 2500.00, # USD ($)
        "kyc_status": "Unverified", # Options: Unverified, Pending, Verified
        "nid_number": "",
        "ref_code": "QX-GLOBAL-99",
        "ref_earnings": 45.00
    }

if "trade_history" not in st.session_state:
    st.session_state.trade_history = [
        {"time": "14:22:10", "asset": "EUR/USD", "mode": "UP (CALL)", "amount": "$100", "payout_pct": "93%", "result": "WIN", "profit": "+$193.00"},
        {"time": "14:15:05", "asset": "GBP/USD", "mode": "EVEN", "amount": "$50", "payout_pct": "93%", "result": "WIN", "profit": "+$96.50"},
        {"time": "14:02:40", "asset": "USD/JPY", "mode": "DOWN (PUT)", "amount": "$100", "payout_pct": "93%", "result": "LOSS", "profit": "-$100.00"},
    ]

if "deposit_requests" not in st.session_state:
    st.session_state.deposit_requests = []

if "withdrawal_requests" not in st.session_state:
    st.session_state.withdrawal_requests = []

# ==========================================
# 3. AUTHENTICATION MODULE (LOGIN / REGISTER)
# ==========================================
def render_auth_screen():
    st.markdown("<h2 class='font-orbitron' style='text-align:center;'>⚡ QUANTX GLOBAL EXCHANGE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Global High-Frequency & Binary Options Trading Terminal</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔒 LOGIN", "📝 REGISTER"])
        
        with auth_tab1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            email_in = st.text_input("Email / Username", value="trader@quantx.io", key="login_email")
            pass_in = st.text_input("Password", type="password", value="123456", key="login_pass")
            if st.button("ENTER TRADING TERMINAL", use_container_width=True):
                st.session_state.authenticated = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with auth_tab2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            reg_user = st.text_input("Desired Username", key="reg_user")
            reg_email = st.text_input("Global Email Address", key="reg_email")
            reg_pass = st.text_input("Create Password", type="password", key="reg_pass")
            reg_ref = st.text_input("Referral Code (Optional)", key="reg_ref")
            
            if st.button("CREATE GLOBAL ACCOUNT", use_container_width=True):
                if reg_user and reg_email:
                    st.session_state.user["username"] = reg_user
                    st.session_state.user["email"] = reg_email
                    st.session_state.authenticated = True
                    st.success("Account created successfully! Welcome to QuantX.")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields.")
            st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.authenticated:
    render_auth_screen()
    st.stop()

# ==========================================
# 4. QUANT DATA & AI CANDLE ENGINE
# ==========================================
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY", "demo")

def fetch_live_candle_data(symbol="EUR/USD", interval="1min", outputsize=60):
    """Fetches real-time market candles or generates high-precision synthetic candles."""
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={TWELVEDATA_API_KEY}"
    try:
        response = requests.get(url, timeout=3)
        data = response.json()
        if "values" in data:
            df = pd.DataFrame(data["values"])
            df["datetime"] = pd.to_datetime(df["datetime"])
            for col in ["open", "high", "low", "close"]:
                df[col] = df[col].astype(float)
            df = df.sort_values("datetime").reset_index(drop=True)
            return df
    except Exception:
        pass

    # High-Precision Fallback Candle Data
    end_time = pd.Timestamp.now()
    dates = pd.date_range(end=end_time, periods=outputsize, freq="1min")
    base_price = 1.0850 if "EUR" in symbol else (150.25 if "JPY" in symbol else 1.2650)
    
    np.random.seed(int(time.time() // 20))
    returns = np.random.normal(0, 0.0002, outputsize)
    price_series = base_price * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        "datetime": dates,
        "open": price_series,
        "high": price_series + np.abs(np.random.normal(0, 0.00015, outputsize)),
        "low": price_series - np.abs(np.random.normal(0, 0.00015, outputsize)),
        "close": price_series + np.random.normal(0, 0.00008, outputsize)
    })
    return df

def process_technical_indicators(df):
    """Calculates EMA 20/50, RSI, Bollinger Bands & MACD."""
    df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['BB_std'] = df['close'].rolling(window=20).std()
    df['BB_Upper'] = df['SMA_20'] + (df['BB_std'] * 2)
    df['BB_Lower'] = df['SMA_20'] - (df['BB_std'] * 2)

    ema_12 = df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    return df

def compute_ai_signals(df):
    """Deep AI Confluence Signal & Odd/Even Candle Analysis Engine."""
    last_candle = df.iloc[-1]
    prev_candle = df.iloc[-2]

    bullish_factors = 0
    bearish_factors = 0
    reasons = []

    # 1. EMA Trend
    if last_candle['EMA_20'] > last_candle['EMA_50']:
        bullish_factors += 30
        reasons.append("EMA 20 Bullish Crossover above EMA 50")
    else:
        bearish_factors += 30
        reasons.append("EMA 20 Bearish Crossover below EMA 50")

    # 2. RSI Reversal
    if last_candle['RSI'] < 30:
        bullish_factors += 35
        reasons.append(f"RSI Oversold ({last_candle['RSI']:.1f}) - Up Reversal Imminent")
    elif last_candle['RSI'] > 70:
        bearish_factors += 35
        reasons.append(f"RSI Overbought ({last_candle['RSI']:.1f}) - Down Reversal Imminent")

    # 3. Bollinger Reversion
    if last_candle['close'] <= last_candle['BB_Lower']:
        bullish_factors += 25
        reasons.append("Price touching Lower Bollinger Band Support")
    elif last_candle['close'] >= last_candle['BB_Upper']:
        bearish_factors += 25
        reasons.append("Price touching Upper Bollinger Band Resistance")

    # Final Precision AI Decision
    if bullish_factors > bearish_factors:
        up_down_signal = "UP (CALL)"
        accuracy = min(98.2, 75.0 + (bullish_factors / 90.0) * 23.2)
        bg_color = "#10b981"
    else:
        up_down_signal = "DOWN (PUT)"
        accuracy = min(98.2, 75.0 + (bearish_factors / 90.0) * 23.2)
        bg_color = "#f43f5e"

    # Candle Odd/Even Digit Logic
    last_price_str = f"{last_candle['close']:.5f}".replace(".", "")
    last_digit = int(last_price_str[-1])
    odd_even_state = "ODD (বিজোর)" if last_digit % 2 != 0 else "EVEN (জোর)"

    return {
        "up_down_signal": up_down_signal,
        "accuracy": round(accuracy, 1),
        "reasons": reasons,
        "bg_color": bg_color,
        "spot_price": last_candle['close'],
        "last_digit": last_digit,
        "odd_even_state": odd_even_state
    }

# ==========================================
# 5. GLOBAL INTERFACE TOP HEADER
# ==========================================
head_col1, head_col2 = st.columns([3, 1.2])

with head_col1:
    st.markdown("""
    <h1 class='font-orbitron' style='font-size: 24px; margin:0;'>
        ⚡ QUANTX <span style='font-size:14px; color:#3b82f6;'>GLOBAL HFT & BINARY TERMINAL</span>
    </h1>
    """, unsafe_allow_html=True)

with head_col2:
    st.markdown(f"""
    <div style="text-align: right; background: rgba(16, 185, 129, 0.1); padding: 8px 14px; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.3);">
        <span style="font-size: 10px; color: #94a3b8; display: block;">LIVE WALLET BALANCE</span>
        <span class="font-orbitron text-green" style="font-size: 18px; font-weight: 800;">${st.session_state.user['balance']:,.2f} USD</span>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ==========================================
# 6. MAIN 4-TAB EXCHANGE LAYOUT
# ==========================================
tab_home, tab_trade, tab_wallet, tab_profile = st.tabs([
    "🏠  HOME", 
    "📈  TRADE TERMINAL (93% PAYOUT)", 
    "💳  WALLET & RECHARGE", 
    "👤  PROFILE & KYC NID"
])

# ------------------------------------------
# TAB 1: HOME
# ------------------------------------------
with tab_home:
    st.markdown("""
    <div class="glass-card" style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9)); border-left: 4px solid #10b981;">
        <h2 class="font-orbitron" style="font-size: 18px; margin-bottom: 6px;">🌍 Global Institutional Binary Options Platform</h2>
        <p style="color: #94a3b8; font-size: 13px; margin: 0;">Execute sub-millisecond Up/Down and Candle Odd/Even trades with guaranteed 93% payouts and 98%+ AI accuracy.</p>
    </div>
    """, unsafe_allow_html=True)

    # Market Ticker
    st.markdown("<h4 class='font-orbitron' style='font-size: 14px; color:#94a3b8;'>LIVE FOREX & OTC MARKETS</h4>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    ticker_data = [
        ("EUR/USD OTC", "1.08542", "+0.42%", "text-green"),
        ("GBP/USD OTC", "1.26410", "-0.18%", "text-red"),
        ("USD/JPY OTC", "150.420", "+0.65%", "text-green"),
        ("AUD/CAD OTC", "0.89215", "+0.22%", "text-green")
    ]
    
    for col, (pair, price, change, c_class) in zip([m1, m2, m3, m4], ticker_data):
        with col:
            st.markdown(f"""
            <div class="glass-card" style="padding: 12px; text-align: center;">
                <span style="font-size: 11px; color: #94a3b8;">{pair}</span>
                <div class="font-orbitron" style="font-size: 16px; font-weight:700; margin: 4px 0;">{price}</div>
                <span class="{c_class}" style="font-size: 12px; font-weight:600;">{change}</span>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    st.markdown("<h4 class='font-orbitron' style='font-size: 14px; color:#94a3b8;'>PLATFORM OVERVIEW</h4>", unsafe_allow_html=True)
    o1, o2, o3 = st.columns(3)
    
    with o1:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <span style="font-size: 12px; color: #94a3b8;">Global Active Traders</span>
            <div class="font-orbitron text-blue" style="font-size: 22px; font-weight:800; margin-top:6px;">128,450</div>
        </div>
        """, unsafe_allow_html=True)
    with o2:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <span style="font-size: 12px; color: #94a3b8;">Trading Profit Payout</span>
            <div class="font-orbitron text-green" style="font-size: 22px; font-weight:800; margin-top:6px;">93% FIX</div>
        </div>
        """, unsafe_allow_html=True)
    with o3:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <span style="font-size: 12px; color: #94a3b8;">24h Executed Volume</span>
            <div class="font-orbitron text-purple" style="font-size: 22px; font-weight:800; margin-top:6px;">$412.5M USD</div>
        </div>
        """, unsafe_allow_html=True)


# ------------------------------------------
# TAB 2: TRADE TERMINAL
# ------------------------------------------
with tab_trade:
    # Asset Selection Row
    ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 1])
    with ctrl1:
        selected_asset = st.selectbox("SELECT ASSET PAIR", ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/CAD"], index=0)
    with ctrl2:
        timeframe = st.selectbox("CANDLE TIMEFRAME", ["1min", "5min"], index=0)
    with ctrl3:
        trade_mode = st.radio("TRADE MODE", ["UP / DOWN (93%)", "ODD / EVEN (93%)"], horizontal=True)

    # Fetch Candle Data & Run AI Engine
    df_candle = fetch_live_candle_data(symbol=selected_asset, interval=timeframe)
    df_candle = process_technical_indicators(df_candle)
    ai_engine = compute_ai_signals(df_candle)

    col_chart, col_panel = st.columns([2.2, 1])

    with col_chart:
        # Interactive Candlestick Plotly Chart
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])

        fig.add_trace(go.Candlestick(
            x=df_candle['datetime'],
            open=df_candle['open'],
            high=df_candle['high'],
            low=df_candle['low'],
            close=df_candle['close'],
            name="Candle"
        ), row=1, col=1)

        fig.add_trace(go.Scatter(x=df_candle['datetime'], y=df_candle['EMA_20'], line=dict(color='#3b82f6', width=1.5), name="EMA 20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_candle['datetime'], y=df_candle['EMA_50'], line=dict(color='#f59e0b', width=1.5), name="EMA 50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_candle['datetime'], y=df_candle['RSI'], line=dict(color='#8b5cf6', width=1.5), name="RSI (14)"), row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(16, 22, 34, 0.5)',
            margin=dict(l=10, r=10, t=10, b=10),
            height=400,
            showlegend=False,
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig, use_container_width=True)

        # Recent Trades Table
        st.markdown("<h4 class='font-orbitron' style='font-size: 13px; color:#94a3b8;'>LIVE EXECUTION HISTORY</h4>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(st.session_state.trade_history), use_container_width=True, hide_index=True)

    with col_panel:
        # AI Confluence Card
        st.markdown(f"""
        <div class="glass-card" style="border: 1px solid {ai_engine['bg_color']};">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size: 10px; color:#94a3b8;">AI CONFLUENCE ENGINE</span>
                <span style="font-size: 11px; font-weight:700; color:{ai_engine['bg_color']}">{ai_engine['accuracy']}% ACCURACY</span>
            </div>
            <div class="font-orbitron" style="font-size: 20px; font-weight:900; color:{ai_engine['bg_color']}; margin: 6px 0;">
                RECOMMENDATION: {ai_engine['up_down_signa
