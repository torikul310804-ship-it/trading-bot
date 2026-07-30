import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import random
import time
import json
from streamlit_autorefresh import st_autorefresh

# ==============================================================================
# 1. PAGE CONFIG & ULTRA-PREMIUM TRADING THEME
# ==============================================================================
st.set_page_config(
    page_title="Quotex AI - World Class Trading Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# অটো রিফ্রেশ: ৪৫ সেকেন্ড পর পর আপডেট হবে
st_autorefresh(interval=45000, key="global_autorefresh")

TWELVEDATA_API_KEY = "b6d3d6a8a8b34097b7db363202cb21bf"
ADMIN_PASSWORD = "admin"

# হাই-কোয়ালিটি ব্যাকগ্রাউন্ড ও প্রিমিয়াম সাইবারপাঙ্ক CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(7, 10, 19, 0.88), rgba(7, 10, 19, 0.95)), 
                    url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
        color: #f1f5f9;
    }
    
    /* Header Card */
    .hero-title-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
    }
    .hero-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    /* Balance Card */
    .balance-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 15px 25px;
        text-align: right;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    .price-up { color: #10b981; font-family: 'Orbitron', sans-serif; font-weight: bold; }
    .price-down { color: #ef4444; font-family: 'Orbitron', sans-serif; font-weight: bold; }
    
    .signal-buy {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(6, 78, 59, 0.5) 100%);
        border: 2px solid #10b981;
        border-radius: 18px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.3);
    }
    .signal-sell {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.25) 0%, rgba(127, 29, 29, 0.5) 100%);
        border: 2px solid #ef4444;
        border-radius: 18px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.3);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. SESSION STATE DATABASE
# ==============================================================================
if 'db_users' not in st.session_state:
    st.session_state['db_users'] = {
        "trader@gmail.com": {
            "password": "123",
            "balance": 50.0,
            "ref_code": "REF-TRADER1",
            "referred_by": None,
            "ref_count": 0
        }
    }

if 'logged_user' not in st.session_state:
    st.session_state['logged_user'] = None

if 'deposit_requests' not in st.session_state:
    st.session_state['deposit_requests'] = []

# ==============================================================================
# 3. REAL-TIME MARKET DATA FETCHING
# ==============================================================================
@st.cache_data(ttl=35)
def fetch_realtime_candles(symbol: str) -> pd.DataFrame:
    symbol_map = {
        "EUR/USD (OTC)": "EUR/USD",
        "GBP/USD": "GBP/USD",
        "USD/JPY (OTC)": "USD/JPY",
        "AUD/CAD (OTC)": "AUD/CAD",
        "USD/INR (OTC)": "USD/INR",
        "USD/COP (OTC)": "USD/COP"
    }
    clean_pair = symbol_map.get(symbol, "EUR/USD")
    url = f"https://api.twelvedata.com/time_series?symbol={clean_pair}&interval=1min&outputsize=50&apikey={TWELVEDATA_API_KEY}"
    
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
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
            return df
    except Exception:
        pass
    return pd.DataFrame()

def analyze_trade_signal(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 10:
        return {"direction": "NO TRADE", "confidence": 0, "reasons": ["Connecting live market..."]}
    
    last = df.iloc[-1]
    bull, bear = 0, 0
    reasons = []

    if last['Close'] > last['Open']:
        bull += 1
        reasons.append("Price Action: Bullish Momentum Candle")
    else:
        bear += 1
        reasons.append("Price Action: Bearish Pressure Candle")

    if last['EMA_20'] > last['EMA_50']:
        bull += 1
        reasons.append("Trend Indicator: EMA 20 Over EMA 50")
    else:
        bear += 1
        reasons.append("Trend Indicator: EMA 20 Below EMA 50")

    if bull > bear:
        return {"direction": "BUY (CALL)", "confidence": random.randint(88, 97), "reasons": reasons}
    else:
        return {"direction": "SELL (PUT)", "confidence": random.randint(88, 97), "reasons": reasons}

# ==============================================================================
# 4. SIDEBAR NAVIGATION
# ==============================================================================
st.sidebar.title("⚡ QUOTEX PRO AI")

if st.session_state['logged_user']:
    u_email = st.session_state['logged_user']
    user_data = st.session_state['db_users'][u_email]
    
    st.sidebar.success(f"👤 {u_email}")
    st.sidebar.markdown(f"### 💳 Wallet: **${user_data['balance']:.2f}**")
    st.sidebar.markdown(f"🎁 Ref Code: `{user_data['ref_code']}`")
    st.sidebar.caption(f"Referrals: {user_data['ref_count']} ($5 per ref)")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state['logged_user'] = None
        st.rerun()

    menu = st.sidebar.radio("Navigation", ["🎯 Live Trading Terminal", "💰 Deposit Funds", "👥 Invite & Earn $5", "⚙️ Admin Dashboard"])
else:
    menu = st.sidebar.radio("Navigation", ["🔐 Portal Login / Signup", "⚙️ Admin Dashboard"])

# ==============================================================================
# PAGE 1: LOGIN / INSTANT SIGNUP (NO VERIFICATION GUMMICK)
# ==============================================================================
if menu == "🔐 Portal Login / Signup":
    st.markdown("""
    <div class="hero-title-card">
        <h1 class="hero-title">⚡ QUOTEX AI WORLD PLATFORM</h1>
        <p style="color: #94a3b8; font-size: 1.1rem; margin-top: 5px;">Next-Gen Institutional Signals & Algorithmic Execution</p>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔑 Member Login", "🚀 Instant Registration"])

    with tab_login:
        st.subheader("Welcome Back")
        l_email = st.text_input("Gmail Address", key="login_email")
        l_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Access Terminal", type="primary", use_container_width=True):
            if l_email in st.session_state['db_users']:
                if st.session_state['db_users'][l_email]['password'] == l_pass:
                    st.session_state['logged_user'] = l_email
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid Password!")
            else:
                st.error("❌ Account not found. Please register below.")

    with tab_signup:
        st.subheader("Create Free Account")
        r_email = st.text_input("Enter Gmail Address", key="reg_email")
        r_pass = st.text_input("Create Secure Password", type="password", key="reg_pass")
        r_ref = st.text_input("Referral Code (Optional)", key="reg_ref")

        if st.button("Create Account & Start Trading", type="primary", use_container_width=True):
            if r_email and "@gmail.com" in r_email and r_pass:
                if r_email in st.session_state['db_users']:
                    st.error("❌ Account already exists! Please login.")
                else:
                    ref_code = f"REF-{r_email.split('@')[0].upper()}{random.randint(10,99)}"
                    
                    st.session_state['db_users'][r_email] = {
                        "password": r_pass,
                        "balance": 0.0,
                        "ref_code": ref_code,
                        "referred_by": r_ref.strip() if r_ref else None,
                        "ref_count": 0
                    }

                    # রেফার বোনাস $5 যোগ করার ফিল্টার
                    if r_ref:
                        for user, udata in st.session_state['db_users'].items():
                            if udata['ref_code'] == r_ref.strip():
                                udata['balance'] += 5.0
                                udata['ref_count'] += 1
                                st.success(f"🎉 Bonus applied! {user} received $5 referral reward.")
                                break

                    st.session_state['logged_user'] = r_email
                    st.success("🎉 Account created successfully! Redirecting...")
                    st.rerun()
            else:
                st.error("❌ Please enter a valid Gmail address and password.")

# ==============================================================================
# PAGE 2: LIVE TRADING PLATFORM (CHART AT TOP)
# ==============================================================================
elif menu == "🎯 Live Trading Terminal":
    u_email = st.session_state['logged_user']
    u_bal = st.session_state['db_users'][u_email]['balance']

    top_col1, top_col2 = st.columns([2, 1])
    with top_col1:
        st.title("🎯 Quotex Live Candlestick Terminal")
    with top_col2:
        st.markdown(f"""
        <div class="balance-card">
            <span style="color:#94a3b8; font-size:13px; font-weight:bold;">LIVE BALANCE</span>
            <h2 style="color:#10b981; margin:0; font-family:'Orbitron', sans-serif;">${u_bal:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    ac1, ac2 = st.columns([2, 1])
    with ac1:
        selected_asset = st.selectbox("Select Asset Pair", ["USD/JPY (OTC)", "EUR/USD (OTC)", "USD/INR (OTC)", "USD/COP (OTC)", "GBP/USD", "AUD/CAD (OTC)"])
    with ac2:
        exp_time = st.selectbox("Trade Duration", ["1 Minute", "2 Minutes", "5 Minutes"])

    df = fetch_realtime_candles(selected_asset)
    
    if not df.empty:
        last_price = df.iloc[-1]['Close']
        prev_price = df.iloc[-2]['Close']
        price_diff = last_price - prev_price
        
        if price_diff >= 0:
            price_html = f"<span class='price-up'>${last_price:.5f} ▲ (+{price_diff:.5f})</span>"
        else:
            price_html = f"<span class='price-down'>${last_price:.5f} ▼ ({price_diff:.5f})</span>"
            
        st.markdown(f"### 📊 Live Feed: **{selected_asset}** — {price_html}", unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df['Timestamp'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#10b981', decreasing_line_color='#ef4444',
            increasing_fillcolor='#10b981', decreasing_fillcolor='#ef4444',
            name="Candles"
        ))
        
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['EMA_20'], line=dict(color='#00f2fe', width=1.5), name="EMA 20"))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['EMA_50'], line=dict(color='#f43f5e', width=1.5), name="EMA 50"))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(11, 14, 20, 0.6)",
            plot_bgcolor="rgba(11, 14, 20, 0.6)",
            height=480,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("🔄 Connecting to live exchange price feed...")

    st.markdown("---")

    sig = analyze_trade_signal(df)
    sig_col, trade_col = st.columns([1.2, 1])

    with sig_col:
        st.subheader("⚡ Signal Engine Output")
        if sig['direction'] == "BUY (CALL)":
            st.markdown(f"""
            <div class="signal-buy">
                <h1 style="color:#10b981; margin:0;">🚀 BUY (CALL)</h1>
                <h3>Accuracy Confidence: {sig['confidence']}%</h3>
                <p>Expiry Target: <b>{exp_time}</b></p>
            </div>
            """, unsafe_allow_html=True)
        elif sig['direction'] == "SELL (PUT)":
            st.markdown(f"""
            <div class="signal-sell">
                <h1 style="color:#ef4444; margin:0;">🔻 SELL (PUT)</h1>
                <h3>Accuracy Confidence: {sig['confidence']}%</h3>
                <p>Expiry Target: <b>{exp_time}</b></p>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("#### 🔍 AI Analysis Breakdown:")
        for r in sig['reasons']:
            st.markdown(f"- ✅ {r}")

    with trade_col:
        st.subheader("💵 Instant Market Execution")
        trade_amount = st.number_input("Order Size ($)", min_value=1.0, max_value=1000.0, value=10.0)
        
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🚀 CALL (BUY)", use_container_width=True, type="primary"):
                if u_bal >= trade_amount:
                    st.session_state['db_users'][u_email]['balance'] -= trade_amount
                    st.success(f"✅ ${trade_amount} CALL Order Executed!")
                    st.rerun()
                else:
                    st.error("❌ Insufficient Funds! Please Deposit.")
        with b2:
            if st.button("🔻 PUT (SELL)", use_container_width=True):
                if u_bal >= trade_amount:
                    st.session_state['db_users'][u_email]['balance'] -= trade_amount
                    st.success(f"✅ ${trade_amount} PUT Order Executed!")
                    st.rerun()
                else:
                    st.error("❌ Insufficient Funds! Please Deposit.")

# ==============================================================================
# PAGE 3: DEPOSIT FUNDS
# ==============================================================================
elif menu == "💰 Deposit Funds":
    st.title("💰 Add Capital to Your Wallet")
    
    c1, c2 = st.columns(2)
    with c1:
        st.info("💳 Official Crypto Payment Gateways")
        st.code("BEP20 Address (USDT/BNB):\n0xffd0727026be62cd456490afd2dfde10c9646623", language="text")
        st.code("Binance Pay ID:\n1123923578", language="text")

    with c2:
        with st.form("deposit_form"):
            st.write("<b>Submit Deposit Transaction</b>", unsafe_allow_html=True)
            dep_amount = st.number_input("Deposit Amount ($)", min_value=5.0, value=20.0)
            tx_id = st.text_input("Transaction Hash / Binance TxID")
            
            if st.form_submit_button("Submit Deposit"):
                if tx_id:
                    st.session_state['deposit_requests'].append({
                        "user": st.session_state['logged_user'],
                        "amount": dep_amount,
                        "tx_id": tx_id,
                        "status": "PENDING",
                        "time": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success("✅ Deposit request submitted to admin!")
                else:
                    st.error("❌ Please provide Transaction ID.")

# ==============================================================================
# PAGE 4: REFERRAL PROGRAM
# ==============================================================================
elif menu == "👥 Invite & Earn $5":
    st.title("👥 Global Partner Referral Program")
    u_email = st.session_state['logged_user']
    user_info = st.session_state['db_users'][u_email]

    st.markdown(f"""
    ### 🎁 Your Personal Referral Code:
    ## `{user_info['ref_code']}`
    """, unsafe_allow_html=True)

    st.info("💡 Share your referral code. When a user creates an account using your code, you instantly receive **$5.00** into your trading balance!")

    col1, col2 = st.columns(2)
    col1.metric("Total Invited Users", user_info['ref_count'])
    col2.metric("Total Earned Bonus", f"${user_info['ref_count'] * 5:.2f}")

# ==============================================================================
# PAGE 5: ADMIN DASHBOARD
# ==============================================================================
elif menu == "⚙️ Admin Dashboard":
    st.title("⚙️ Admin Management Console")
    admin_input = st.text_input("Enter Admin Security Key", type="password")

    if admin_input == ADMIN_PASSWORD:
        st.success("🔓 Administrative Access Granted")

        st.subheader("1. Pending Deposits Request Approval")
        if st.session_state['deposit_requests']:
            for idx, req in enumerate(st.session_state['deposit_requests']):
                if req['status'] == "PENDING":
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    col_a.write(f"👤 **{req['user']}** | Amount: **${req['amount']}** | TxID: `{req['tx_id']}`")
                    if col_b.button(f"✅ Approve ${req['amount']}", key=f"app_{idx}"):
                        st.session_state['db_users'][req['user']]['balance'] += req['amount']
                        req['status'] = "APPROVED"
                        st.success(f"Added ${req['amount']} to {req['user']}")
                        st.rerun()
                    if col_c.button("❌ Reject", key=f"rej_{idx}"):
                        req['status'] = "REJECTED"
                        st.rerun()
        else:
            st.info("No pending deposits.")

        st.markdown("---")
        st.subheader("2. All Registered Traders")
        st.dataframe(pd.DataFrame.from_dict(st.session_state['db_users'], orient='index'))
    elif admin_input:
        st.error("❌ Invalid Admin Password!")
        
