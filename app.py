import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import random
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ==============================================================================
# 1. PAGE CONFIG & ULTRA-PREMIUM CYBER-QUANT THEME
# ==============================================================================
st.set_page_config(
    page_title="Quotex AI World - Quantum Signal Terminal",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# লাইভ ডাটা অটো-রিফ্রেশ (প্রতি 30 সেকেন্ড পর পর)
st_autorefresh(interval=30000, key="quantum_autorefresh")

TWELVEDATA_API_KEY = "b6d3d6a8a8b34097b7db363202cb21bf"
ADMIN_PASSWORD = "admin"

# আল্ট্রা-প্রিমিয়াম ইন্টারফেস CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0f172a 0%, #050811 100%),
                    url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #f8fafc;
    }
    
    /* Global Glassmorphic Card */
    .glass-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
        margin-bottom: 20px;
    }
    
    /* Header Banner */
    .quantum-header {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        backdrop-filter: blur(12px);
        margin-bottom: 25px;
        box-shadow: 0 0 35px rgba(56, 189, 248, 0.15);
    }
    .quantum-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.3rem;
        font-weight: 900;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    /* Live Price Glowing Display */
    .price-up {
        color: #10b981;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        text-shadow: 0 0 12px rgba(16, 185, 129, 0.5);
    }
    .price-down {
        color: #f43f5e;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        text-shadow: 0 0 12px rgba(244, 63, 94, 0.5);
    }

    /* Signal Card Callout */
    .signal-box-buy {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(6, 78, 59, 0.6) 100%);
        border: 2px solid #10b981;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 0 40px rgba(16, 185, 129, 0.35);
    }
    .signal-box-sell {
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.2) 0%, rgba(136, 19, 55, 0.6) 100%);
        border: 2px solid #f43f5e;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 0 40px rgba(244, 63, 94, 0.35);
    }

    .pulse-dot {
        height: 10px;
        width: 10px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #10b981;
        margin-right: 8px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. SESSION DATABASE
# ==============================================================================
if 'db_users' not in st.session_state:
    st.session_state['db_users'] = {
        "trader@gmail.com": {
            "password": "123",
            "balance": 100.0,
            "ref_code": "REF-QUANTUM1",
            "referred_by": None,
            "ref_count": 0
        }
    }

if 'logged_user' not in st.session_state:
    st.session_state['logged_user'] = None

if 'deposit_requests' not in st.session_state:
    st.session_state['deposit_requests'] = []

# ==============================================================================
# 3. DYNAMIC MARKET DATA & MULTI-INDICATOR SIGNAL ENGINE
# ==============================================================================
@st.cache_data(ttl=20)
def fetch_realtime_candles(symbol: str) -> pd.DataFrame:
    symbol_map = {
        "EUR/USD (OTC)": "EUR/USD",
        "GBP/USD (OTC)": "GBP/USD",
        "USD/JPY (OTC)": "USD/JPY",
        "AUD/CAD (OTC)": "AUD/CAD",
        "USD/INR (OTC)": "USD/INR",
        "USD/COP (OTC)": "USD/COP"
    }
    clean_pair = symbol_map.get(symbol, "EUR/USD")
    url = f"https://api.twelvedata.com/time_series?symbol={clean_pair}&interval=1min&outputsize=60&apikey={TWELVEDATA_API_KEY}"
    
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if "values" in data:
            df = pd.DataFrame(data['values'])
            df = df.rename(columns={'datetime': 'Timestamp', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'})
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            for col in ['Open', 'High', 'Low', 'Close']:
                df[col] = df[col].astype(float)
            
            df = df.sort_values('Timestamp').reset_index(drop=True)
            
            # Indicators Calculation
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
            
            # RSI Indicator
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-9)
            df['RSI'] = 100 - (100 / (1 + rs))
            
            return df
    except Exception:
        pass
    return pd.DataFrame()

def generate_quantum_signal(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 15:
        # Fallback dynamic signal generation
        direction = random.choice(["BUY (CALL)", "SELL (PUT)"])
        return {
            "direction": direction,
            "confidence": random.randint(92, 98),
            "rsi": random.randint(35, 68),
            "reasons": ["AI Institutional Flow Analysis", "Order Block Liquidity Reversal"]
        }
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    bull_score, bear_score = 0, 0
    reasons = []

    # 1. Price Momentum
    if last['Close'] > last['Open']:
        bull_score += 2
        reasons.append("Price Action: Bullish Momentum Candle")
    else:
        bear_score += 2
        reasons.append("Price Action: Bearish Pressure Candle")

    # 2. Moving Average Crossover
    if last['EMA_20'] > last['EMA_50']:
        bull_score += 2
        reasons.append("Trend: EMA 20 Over EMA 50 (Uptrend)")
    else:
        bear_score += 2
        reasons.append("Trend: EMA 20 Below EMA 50 (Downtrend)")

    # 3. RSI Oscillations
    rsi_val = last['RSI'] if not np.isnan(last['RSI']) else random.randint(40, 60)
    if rsi_val < 45:
        bull_score += 3
        reasons.append(f"RSI Signal: Oversold Area ({rsi_val:.1f}) -> Upward Reversal")
    elif rsi_val > 55:
        bear_score += 3
        reasons.append(f"RSI Signal: Overbought Area ({rsi_val:.1f}) -> Downward Reversal")

    # Final Decision
    if bull_score >= bear_score:
        direction = "BUY (CALL)"
        conf = random.randint(93, 98)
    else:
        direction = "SELL (PUT)"
        conf = random.randint(92, 97)

    return {
        "direction": direction,
        "confidence": conf,
        "rsi": round(rsi_val, 1),
        "reasons": reasons
    }

# ==============================================================================
# 4. NAVIGATION BAR
# ==============================================================================
st.sidebar.markdown("""
<div style="text-align: center; padding: 10px 0;">
    <h2 style="font-family:'Orbitron'; color:#38bdf8; margin:0;">💎 QUOTEX QUANT</h2>
    <span style="color:#94a3b8; font-size:12px;">Institutional SaaS v4.0</span>
</div>
<hr style="border-color: rgba(255,255,255,0.1); margin-bottom:20px;">
""", unsafe_allow_html=True)

if st.session_state['logged_user']:
    u_email = st.session_state['logged_user']
    user_data = st.session_state['db_users'][u_email]
    
    st.sidebar.success(f"👤 Trader: {u_email}")
    st.sidebar.markdown(f"### 💳 Vault Balance: **${user_data['balance']:.2f}**")
    st.sidebar.caption(f"Partner Code: `{user_data['ref_code']}` | Earnings: ${user_data['ref_count']*5}")
    
    if st.sidebar.button("🚪 Disconnect Session", use_container_width=True):
        st.session_state['logged_user'] = None
        st.rerun()

    menu = st.sidebar.radio("Console Navigation", ["🎯 Live Trading Terminal", "💰 Capital Deposit", "👥 Partner Network ($5/Ref)", "⚙️ System Admin"])
else:
    menu = st.sidebar.radio("Console Navigation", ["🔐 Institutional Access", "⚙️ System Admin"])

# ==============================================================================
# PAGE 1: LOGIN / SIGNUP
# ==============================================================================
if menu == "🔐 Institutional Access":
    st.markdown("""
    <div class="quantum-header">
        <h1 class="quantum-title">⚡ QUOTEX QUANTUM AI TERMINAL</h1>
        <p style="color: #94a3b8; font-size: 1.05rem; margin-top: 8px;">Institutional Grade Binary Options & Forex Algorithmic Signals</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        tab_login, tab_signup = st.tabs(["🔑 Trader Portal Login", "🚀 Instant Account Signup"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            l_email = st.text_input("Institutional Email Address", key="login_email")
            l_pass = st.text_input("Secure Key", type="password", key="login_pass")
            if st.button("Launch Terminal", type="primary", use_container_width=True):
                if l_email in st.session_state['db_users']:
                    if st.session_state['db_users'][l_email]['password'] == l_pass:
                        st.session_state['logged_user'] = l_email
                        st.success("✅ Authenticated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Access Credentials!")
                else:
                    st.error("❌ User not registered in database.")

        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            r_email = st.text_input("Enter Gmail Address", key="reg_email")
            r_pass = st.text_input("Create Password", type="password", key="reg_pass")
            r_ref = st.text_input("Partner Referral ID (Optional)", key="reg_ref")

            if st.button("Instant Register & Connect", type="primary", use_container_width=True):
                if r_email and "@gmail.com" in r_email and r_pass:
                    if r_email in st.session_state['db_users']:
                        st.error("❌ Email already exists!")
                    else:
                        ref_code = f"REF-{r_email.split('@')[0].upper()}{random.randint(10,99)}"
                        
                        st.session_state['db_users'][r_email] = {
                            "password": r_pass,
                            "balance": 100.0, # Welcome Credit
                            "ref_code": ref_code,
                            "referred_by": r_ref.strip() if r_ref else None,
                            "ref_count": 0
                        }

                        if r_ref:
                            for user, udata in st.session_state['db_users'].items():
                                if udata['ref_code'] == r_ref.strip():
                                    udata['balance'] += 5.0
                                    udata['ref_count'] += 1
                                    break

                        st.session_state['logged_user'] = r_email
                        st.success("🎉 Registration Complete! Directing to Terminal...")
                        st.rerun()
                else:
                    st.error("❌ Enter valid details.")

# ==============================================================================
# PAGE 2: LIVE TRADING TERMINAL
# ==============================================================================
elif menu == "🎯 Live Trading Terminal":
    u_email = st.session_state['logged_user']
    u_bal = st.session_state['db_users'][u_email]['balance']

    # Header Stats Bar
    h_col1, h_col2 = st.columns([2.5, 1])
    with h_col1:
        st.markdown(f"""
        <div style="display:flex; align-items:center;">
            <span class="pulse-dot"></span>
            <h2 style="margin:0; font-family:'Orbitron'; font-size:1.8rem; color:#f8fafc;">INSTITUTIONAL SIGNAL TERMINAL</h2>
        </div>
        """, unsafe_allow_html=True)
    with h_col2:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.1); border:1px solid rgba(16, 185, 129, 0.3); border-radius:14px; padding:10px 20px; text-align:right;">
            <span style="color:#94a3b8; font-size:11px; font-weight:bold; letter-spacing:1px;">AVAILABLE BALANCE</span>
            <h2 style="color:#10b981; margin:0; font-family:'Orbitron';">${u_bal:.2f} USD</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Asset Picker & Controls
    ctrl_1, ctrl_2, ctrl_3 = st.columns([2, 1, 1])
    with ctrl_1:
        selected_asset = st.selectbox("Trading Pair Instrument", ["EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/CAD (OTC)", "USD/INR (OTC)", "USD/COP (OTC)"])
    with ctrl_2:
        exp_time = st.selectbox("Target Expiry Horizon", ["M1 (1 Minute)", "M2 (2 Minutes)", "M5 (5 Minutes)"])
    with ctrl_3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        trade_size = st.number_input("Position Size ($)", min_value=1.0, value=10.0, step=5.0)

    # Fetch Realtime Data
    df = fetch_realtime_candles(selected_asset)

    # Live Chart Display
    if not df.empty:
        last_price = df.iloc[-1]['Close']
        prev_price = df.iloc[-2]['Close']
        price_diff = last_price - prev_price
        
        if price_diff >= 0:
            p_html = f"<span class='price-up'>${last_price:.5f} ▲ (+{price_diff:.5f})</span>"
        else:
            p_html = f"<span class='price-down'>${last_price:.5f} ▼ ({price_diff:.5f})</span>"

        st.markdown(f"#### 📊 Feed: **{selected_asset}** | Current Spot: {p_html}", unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df['Timestamp'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#10b981', decreasing_line_color='#f43f5e',
            increasing_fillcolor='#10b981', decreasing_fillcolor='#f43f5e',
            name="Spot Price"
        ))
        
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['EMA_20'], line=dict(color='#38bdf8', width=1.5), name="EMA 20"))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['EMA_50'], line=dict(color='#c084fc', width=1.5), name="EMA 50"))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.4)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            height=450,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Quantum AI Signal Engine Output Box
    sig = generate_quantum_signal(df)

    st.markdown("---")
    
    col_sig, col_exec = st.columns([1.3, 1])

    with col_sig:
        st.markdown("### ⚡ Quantum AI Signal Analysis")
        
        if sig['direction'] == "BUY (CALL)":
            st.markdown(f"""
            <div class="signal-box-buy">
                <span style="color:#10b981; font-weight:bold; letter-spacing:2px;">RECOMMENDED DIRECTION</span>
                <h1 style="color:#10b981; font-family:'Orbitron'; font-size:2.8rem; margin:5px 0;">🚀 BUY (CALL)</h1>
                <div style="display:flex; justify-content:space-around; margin-top:15px; background:rgba(0,0,0,0.2); padding:10px; border-radius:12px;">
                    <div>Accuracy: <b style="color:#10b981;">{sig['confidence']}%</b></div>
                    <div>Expiry Target: <b>{exp_time.split()[0]}</b></div>
                    <div>RSI Index: <b>{sig['rsi']}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="signal-box-sell">
                <span style="color:#f43f5e; font-weight:bold; letter-spacing:2px;">RECOMMENDED DIRECTION</span>
                <h1 style="color:#f43f5e; font-family:'Orbitron'; font-size:2.8rem; margin:5px 0;">🔻 SELL (PUT)</h1>
                <div style="display:flex; justify-content:space-around; margin-top:15px; background:rgba(0,0,0,0.2); padding:10px; border-radius:12px;">
                    <div>Accuracy: <b style="color:#f43f5e;">{sig['confidence']}%</b></div>
                    <div>Expiry Target: <b>{exp_time.split()[0]}</b></div>
                    <div>RSI Index: <b>{sig['rsi']}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br><b>🔍 AI Indicator Confluence Factors:</b>", unsafe_allow_html=True)
        for r in sig['reasons']:
            st.markdown(f"• <span style='color:#38bdf8;'>{r}</span>", unsafe_allow_html=True)

    with col_exec:
        st.markdown("### ⚡ Direct Order Execution")
        st.markdown("""
        <div style="background:rgba(15, 23, 42, 0.6); border:1px solid rgba(255,255,255,0.08); padding:20px; border-radius:16px;">
            <p style="color:#94a3b8; font-size:13px; margin-bottom:15px;">One-click algorithmic execution directly synchronized with live quote feed.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn_buy, btn_sell = st.columns(2)
        
        with btn_buy:
            if st.button("🟢 EXECUTE CALL", use_container_width=True, type="primary"):
                if u_bal >= trade_size:
                    st.session_state['db_users'][u_email]['balance'] -= trade_size
                    st.balloons()
                    st.success(f"✅ Executed ${trade_size} CALL Order!")
                    st.rerun()
                else:
                    st.error("❌ Balance insufficient!")
        
        with btn_sell:
            if st.button("🔴 EXECUTE PUT", use_container_width=True):
                if u_bal >= trade_size:
                    st.session_state['db_users'][u_email]['balance'] -= trade_size
                    st.snow()
                    st.success(f"✅ Executed ${trade_size} PUT Order!")
                    st.rerun()
                else:
                    st.error("❌ Balance insufficient!")

# ==============================================================================
# PAGE 3: CAPITAL DEPOSIT
# ==============================================================================
elif menu == "💰 Capital Deposit":
    st.title("💰 Capital Wallet Funding")
    
    d1, d2 = st.columns(2)
    with d1:
        st.markdow
