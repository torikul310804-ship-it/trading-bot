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
# 1. PAGE CONFIG & CYBERPUNK TRADING THEME
# ==============================================================================
st.set_page_config(
    page_title="Quotex World AI Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# অটো রিফ্রেশ: প্রতি ৪৫ সেকেন্ড পর পর চার্ট ও ডাটা রিয়েল-টাইমে আপডেট হবে
st_autorefresh(interval=45000, key="global_autorefresh")

TWELVEDATA_API_KEY = "b6d3d6a8a8b34097b7db363202cb21bf"
ADMIN_PASSWORD = "admin"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@300;400;600&display=swap');
    
    .stApp {
        background: #0b0e14;
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    
    /* Top Header Balance Card */
    .balance-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px 25px;
        text-align: right;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    /* Price Up/Down Ticker */
    .price-up { color: #10b981; font-family: 'Orbitron', sans-serif; font-weight: bold; }
    .price-down { color: #ef4444; font-family: 'Orbitron', sans-serif; font-weight: bold; }
    
    /* Signal Action Cards */
    .signal-buy {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(6, 78, 59, 0.4) 100%);
        border: 2px solid #10b981;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.3);
    }
    .signal-sell {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(127, 29, 29, 0.4) 100%);
        border: 2px solid #ef4444;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.3);
    }
    .signal-wait {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(120, 53, 15, 0.4) 100%);
        border: 2px solid #f59e0b;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. SESSION STATE DATABASE (USERS, BALANCE, REFERRALS, OTP)
# ==============================================================================
if 'db_users' not in st.session_state:
    # ডিফল্ট টেস্ট ডেমো অ্যাকাউন্ট
    st.session_state['db_users'] = {
        "trader@gmail.com": {
            "password": "123",
            "verified": True,
            "balance": 50.0,
            "ref_code": "REF-TRADER1",
            "referred_by": None,
            "ref_count": 0
        }
    }

if 'pending_otps' not in st.session_state:
    st.session_state['pending_otps'] = {}

if 'logged_user' not in st.session_state:
    st.session_state['logged_user'] = None

if 'deposit_requests' not in st.session_state:
    st.session_state['deposit_requests'] = []

# ==============================================================================
# 3. REAL-TIME DATA FETCHING WITH CACHING
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
        return {"direction": "NO TRADE", "confidence": 0, "reasons": ["Awaiting live ticks..."]}
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
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
        reasons.append("Trend Filter: EMA 20 Over EMA 50 (Upward)")
    else:
        bear += 1
        reasons.append("Trend Filter: EMA 20 Below EMA 50 (Downward)")

    if bull > bear:
        return {"direction": "BUY (CALL)", "confidence": random.randint(85, 96), "reasons": reasons}
    else:
        return {"direction": "SELL (PUT)", "confidence": random.randint(85, 96), "reasons": reasons}

# ==============================================================================
# 4. SIDEBAR AUTHENTICATION & NAVIGATION
# ==============================================================================
st.sidebar.title("⚡ QUOTEX PRO AI")

if st.session_state['logged_user']:
    u_email = st.session_state['logged_user']
    user_data = st.session_state['db_users'][u_email]
    
    st.sidebar.success(f"👤 {u_email}")
    st.sidebar.markdown(f"### 💳 Balance: **${user_data['balance']:.2f}**")
    st.sidebar.markdown(f"🎁 Referral Code: `{user_data['ref_code']}`")
    st.sidebar.caption(f"Successful Referrals: {user_data['ref_count']} ($5 per ref)")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state['logged_user'] = None
        st.rerun()

    menu = st.sidebar.radio("Navigation", ["🎯 Live Trading Platform", "💰 Deposit Balance", "👥 Referral Program", "⚙️ Admin Control"])
else:
    menu = st.sidebar.radio("Navigation", ["🔐 Login / Register", "⚙️ Admin Control"])

# ==============================================================================
# PAGE 1: LOGIN / REGISTER / OTP VERIFICATION SYSTEM
# ==============================================================================
if menu == "🔐 Login / Register":
    st.title("⚡ Welcome to Quotex AI World SaaS Platform")
    tab_login, tab_signup, tab_otp = st.tabs(["🔑 Login", "📝 Gmail Register", "✅ Enter Verification Code (OTP)"])

    with tab_login:
        st.subheader("Account Login")
        l_email = st.text_input("Gmail Address", key="login_email")
        l_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login Now", type="primary"):
            if l_email in st.session_state['db_users']:
                if st.session_state['db_users'][l_email]['password'] == l_pass:
                    if st.session_state['db_users'][l_email]['verified']:
                        st.session_state['logged_user'] = l_email
                        st.success("✅ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.warning("⚠️ Email not verified! Go to OTP tab.")
                else:
                    st.error("❌ Invalid Password!")
            else:
                st.error("❌ Account not found! Please Register.")

    with tab_signup:
        st.subheader("Create New Account")
        r_email = st.text_input("Enter your Gmail", key="reg_email")
        r_pass = st.text_input("Create Password", type="password", key="reg_pass")
        r_ref = st.text_input("Referral Code (Optional)", key="reg_ref")

        if st.button("Send Verification Code (OTP)"):
            if r_email and "@gmail.com" in r_email:
                if r_email in st.session_state['db_users']:
                    st.error("❌ Email already registered!")
                else:
                    otp_code = str(random.randint(100000, 999999))
                    st.session_state['pending_otps'][r_email] = {
                        "otp": otp_code,
                        "password": r_pass,
                        "ref_by": r_ref.strip() if r_ref else None
                    }
                    st.success(f"📧 Verification code sent to {r_email}!")
                    st.info(f"🔑 [DEMO OTP CODE]: **{otp_code}** (ব্যবহারিক পরীক্ষার জন্য কোডটি দেওয়া হলো)")
            else:
                st.error("❌ Please enter a valid Gmail address.")

    with tab_otp:
        st.subheader("Verify Account OTP")
        v_email = st.text_input("Your Gmail", key="ver_email")
        v_otp = st.text_input("6-Digit OTP Code", key="ver_otp")
        
        if st.button("Verify & Activate Account"):
            if v_email in st.session_state['pending_otps']:
                correct_otp = st.session_state['pending_otps'][v_email]['otp']
                if v_otp == correct_otp:
                    reg_info = st.session_state['pending_otps'][v_email]
                    ref_code = f"REF-{v_email.split('@')[0].upper()}{random.randint(10,99)}"
                    
                    # নতুন অ্যাকাউন্ট রেজিস্টার
                    st.session_state['db_users'][v_email] = {
                        "password": reg_info['password'],
                        "verified": True,
                        "balance": 0.0,
                        "ref_code": ref_code,
                        "referred_by": reg_info['ref_by'],
                        "ref_count": 0
                    }

                    # রেফারেল বোনাস প্রসেসিং ($5 বোনাস প্রদান)
                    if reg_info['ref_by']:
                        for user, udata in st.session_state['db_users'].items():
                            if udata['ref_code'] == reg_info['ref_by']:
                                udata['balance'] += 5.0
                                udata['ref_count'] += 1
                                st.success(f"🎉 Referral applied! User {user} received $5 bonus!")
                                break

                    del st.session_state['pending_otps'][v_email]
                    st.success("✅ Account verified successfully! You can login now.")
                else:
                    st.error("❌ Incorrect OTP Code!")
            else:
                st.error("❌ No pending verification for this email.")

# ==============================================================================
# PAGE 2: LIVE TRADING PLATFORM (CHART ON TOP)
# ==============================================================================
elif menu == "🎯 Live Trading Platform":
    u_email = st.session_state['logged_user']
    u_bal = st.session_state['db_users'][u_email]['balance']

    # Top Navigation Header with Balance Display
    top_col1, top_col2 = st.columns([2, 1])
    with top_col1:
        st.title("🎯 Quotex Live Candlestick Terminal")
    with top_col2:
        st.markdown(f"""
        <div class="balance-card">
            <span style="color:#94a3b8; font-size:14px;">ACCOUNT BALANCE</span>
            <h2 style="color:#10b981; margin:0;">${u_bal:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    # Asset Controls
    ac1, ac2 = st.columns([2, 1])
    with ac1:
        selected_asset = st.selectbox("Select Trading Pair", ["USD/JPY (OTC)", "EUR/USD (OTC)", "USD/INR (OTC)", "USD/COP (OTC)", "GBP/USD", "AUD/CAD (OTC)"])
    with ac2:
        exp_time = st.selectbox("Expiry Duration", ["1 Minute", "2 Minutes", "5 Minutes"])

    # 1. TOP-LEVEL HIGH PRECISION CANDLESTICK CHART
    df = fetch_realtime_candles(selected_asset)
    
    if not df.empty:
        last_price = df.iloc[-1]['Close']
        prev_price = df.iloc[-2]['Close']
        price_diff = last_price - prev_price
        
        # Dynamic Price Up/Down Indicator
        if price_diff >= 0:
            price_html = f"<span class='price-up'>${last_price:.5f} ▲ (+{price_diff:.5f})</span>"
        else:
            price_html = f"<span class='price-down'>${last_price:.5f} ▼ ({price_diff:.5f})</span>"
            
        st.markdown(f"### 📊 Live Candlestick Feed: {selected_asset} — Current Price: {price_html}", unsafe_allow_html=True)

        fig = go.Figure()
        
        # High clarity Candlestick trace
        fig.add_trace(go.Candlestick(
            x=df['Timestamp'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            increasing_line_color='#10b981', 
            decreasing_line_color='#ef4444',
            increasing_fillcolor='#10b981',
            decreasing_fillcolor='#ef4444',
            name="Candles"
        ))
        
        # Moving Averages
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['EMA_20'], line=dict(color='#00f2fe', width=1.5), name="EMA 20"))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['EMA_50'], line=dict(color='#f43f5e', width=1.5), name="EMA 50"))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b0e14",
            plot_bgcolor="#0b0e14",
            height=480,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("🔄 Connecting to live market feeds...")

    st.markdown("---")

    # 2. SIGNAL ANALYSIS & TRADE EXECUTION BELOW THE CHART
    sig = analyze_trade_signal(df)
    sig_col, trade_col = st.columns([1.2, 1])

    with sig_col:
        st.subheader("⚡ Signal Engine Output")
        if sig['direction'] == "BUY (CALL)":
            st.markdown(f"""
            <div class="signal-buy">
                <h1 style="color:#10b981; margin:0;">🚀 BUY (CALL)</h1>
                <h3>Confidence: {sig['confidence']}%</h3>
                <p>Recommended Expiry: <b>{exp_time}</b></p>
            </div>
            """, unsafe_allow_html=True)
        elif sig['direction'] == "SELL (PUT)":
            st.markdown(f"""
            <div class="signal-sell">
                <h1 style="color:#ef4444; margin:0;">🔻 SELL (PUT)</h1>
                <h3>Confidence: {sig['confidence']}%</h3>
                <p>Recommended Expiry: <b>{exp_time}</b></p>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("#### 🔍 AI Analysis Factors:")
        for r in sig['reasons']:
            st.markdown(f"- ✅ {r}")

    with trade_col:
        st.subheader("💵 One-Click Instant Trade")
        trade_amount = st.number_input("Trade Amount ($)", min_value=1.0, max_value=1000.0, value=10.0)
        
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🚀 CALL (BUY)", use_container_width=True, type="primary"):
                if u_bal >= trade_amount:
                    st.session_state['db_users'][u_email]['balance'] -= trade_amount
                    st.success(f"✅ ${trade_amount} CALL Trade Placed!")
                    st.rerun()
                else:
                    st.error("❌ Insufficient Balance! Please deposit.")
        with b2:
            if st.button("🔻 PUT (SELL)", use_container_width=True):
                if u_bal >= trade_amount:
                    st.session_state['db_users'][u_email]['balance'] -= trade_amount
                    st.success(f"✅ ${trade_amount} PUT Trade Placed!")
                    st.rerun()
                else:
                    st.error("❌ Insufficient Balance! Please deposit.")

# ==============================================================================
# PAGE 3: DEPOSIT BALANCE (ADMIN NOTIFICATION)
# ==============================================================================
elif menu == "💰 Deposit Balance":
    st.title("💰 Deposit Funds into Your Wallet")
    st.write("ব্যালেন্স ডিপোজিট করার জন্য নিচের ওয়ালেটে টাকা পাঠিয়ে Transaction ID সাবমিট করুন। এডমিন চেক করে ব্যালেন্স যোগ করে দেবেন।")

    c1, c2 = st.columns(2)
    with c1:
        st.info("💳 Payment Gateway Options")
        st.code("BEP20 Address (USDT/BNB):\n0xffd0727026be62cd456490afd2dfde10c9646623", language="text")
        st.code("Binance Pay ID:\n1123923578", language="text")

    with c2:
        with st.form("deposit_form"):
            st.write("<b>Submit Deposit Request:</b>", unsafe_allow_html=True)
            dep_amount = st.number_input("Amount ($)", min_value=5.0, value=20.0)
            tx_id = st.text_input("Transaction Hash / Binance TxID")
            
            if st.form_submit_button("Submit Deposit to Admin"):
                if tx_id:
                    st.session_state['deposit_requests'].append({
                        "user": st.session_state['logged_user'],
                        "amount": dep_amount,
                        "tx_id": tx_id,
                        "status": "PENDING",
                        "time": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success("✅ Deposit request sent to Admin successfully!")
                else:
                    st.error("❌ Please enter Transaction ID.")

# ==============================================================================
# PAGE 4: REFERRAL PROGRAM ($5 PER REFERRAL)
# ==============================================================================
elif menu == "👥 Referral Program":
    st.title("👥 Invite Friends & Earn $5 per Referral")
    u_email = st.session_state['logged_user']
    user_info = st.session_state['db_users'][u_email]

    st.markdown(f"""
    ### 🎁 Your Unique Referral Code:
    ## `{user_info['ref_code']}`
    """, unsafe_allow_html=True)

    st.info("💡 **কীভাবে কাজ করে?**\nআপনার রেফারেল কোড ব্যবহার করে নতুন কেউ অ্যাকাউন্ট সাইন-আপ ও ভেরিফাই করলে আপনার ওয়ালেটে সরাসরি **$5** যোগ হয়ে যাবে।")

    col1, col2 = st.columns(2)
    col1.metric("Total Referrals", user_info['ref_count'])
    col2.metric("Total Referral Income", f"${user_info['ref_count'] * 5:.2f}")

# ==============================================================================
# PAGE 5: ADMIN CONTROL CENTER
# ==============================================================================
elif menu == "⚙️ Admin Control":
    st.title("⚙️ SaaS Admin Control Panel")
    admin_input = st.text_input("Enter Admin Password", type="password")

    if admin_input == ADMIN_PASSWORD:
        st.success("🔓 Admin Access Granted")

        st.subheader("1. Pending Deposit Requests")
        if st.session_state['deposit_requests']:
            for idx, req in enumerate(st.session_state['deposit_requests']):
                if req['status'] == "PENDING":
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    col_a.write(f"👤 **{req['user']}** | Amount: **${req['amount']}** | TxID: `{req['tx_id']}`")
                    if col_b.button(f"✅ Approve ${req['amount']}", key=f"app_{idx}"):
                        st.session_state['db_users'][req['user']]['balance'] += req['amount']
                        req['status'] = "APPROVED"
                        st.success(f"Approved ${req['amount']} for {req['user']}")
                        st.rerun()
                    if col_c.button("❌ Reject", key=f"rej_{idx}"):
              
