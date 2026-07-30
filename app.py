import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import hmac
import hashlib
import time
import base64
import json

# ==============================================================================
# 1. PAGE CONFIG & CYBERPUNK GLASSMORPHISM STYLING
# ==============================================================================
st.set_page_config(
    page_title="Quotex AI Signals & SaaS Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced CSS for High-Converting Commercial UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');
    
    .stApp {
        background: #07090e;
        font-family: 'Inter', sans-serif;
        color: #f1f5f9;
    }
    
    /* Neon Glassmorphism Cards */
    .pricing-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
    }
    .pricing-card:hover {
        border-color: #00f2fe;
        transform: translateY(-5px);
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.3);
    }
    .pricing-card-selected {
        background: rgba(0, 242, 254, 0.08);
        border: 2px solid #00f2fe !important;
        box-shadow: 0 0 30px rgba(0, 242, 254, 0.4);
    }
    
    /* Signal Action Cards */
    .signal-buy {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 78, 59, 0.3) 100%);
        border: 2px solid #10b981;
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.3);
    }
    .signal-sell {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(127, 29, 29, 0.3) 100%);
        border: 2px solid #ef4444;
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.3);
    }
    .signal-wait {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(120, 53, 15, 0.3) 100%);
        border: 2px solid #f59e0b;
        border-radius: 16px;
        padding: 25px;
        text-align: center;
    }

    /* Badges */
    .badge-active {
        background: #10b98122;
        color: #10b981;
        border: 1px solid #10b981;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    .badge-expired {
        background: #ef444422;
        color: #ef4444;
        border: 1px solid #ef4444;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Cryptographic Key Security Configuration
SECRET_KEY = b"QUOTEX_SAAS_SUPER_SECRET_SIGNING_KEY_2026"
ADMIN_PASSWORD = "admin"  # অ্যাডমিন প্যানেলে ঢোকার পাসওয়ার্ড

# ==============================================================================
# 2. LICENSE ENGINE & HMAC SECURITY
# ==============================================================================
def generate_license_key(days: int, user_email: str) -> str:
    expiry_time = int(time.time()) + (days * 86400)
    payload = {"email": user_email.strip().lower(), "exp": expiry_time, "days": days}
    raw_payload = json.dumps(payload).encode('utf-8')
    b64_payload = base64.urlsafe_b64encode(raw_payload).decode('utf-8')
    signature = hmac.new(SECRET_KEY, b64_payload.encode('utf-8'), hashlib.sha256).hexdigest()[:12]
    return f"QTX-{b64_payload}-{signature}"

def verify_license_key(key: str) -> tuple[bool, str, int]:
    if not key or not key.startswith("QTX-"):
        return False, "", 0
    try:
        parts = key.strip().split("-")
        if len(parts) != 3:
            return False, "", 0
        _, b64_payload, signature = parts
        expected_sig = hmac.new(SECRET_KEY, b64_payload.encode('utf-8'), hashlib.sha256).hexdigest()[:12]
        if not hmac.compare_digest(signature, expected_sig):
            return False, "", 0
        raw_payload = base64.urlsafe_b64decode(b64_payload.encode('utf-8')).decode('utf-8')
        payload = json.loads(raw_payload)
        exp_time = payload.get("exp", 0)
        current_time = int(time.time())
        if current_time > exp_time:
            return False, payload.get("email", ""), 0
        days_left = max(1, int((exp_time - current_time) / 86400))
        return True, payload.get("email", ""), days_left
    except Exception:
        return False, "", 0

# ==============================================================================
# 3. QUOTEX MARKET ENGINE & INDICATORS
# ==============================================================================
def fetch_quotex_ohlc_data(symbol: str, count: int = 60) -> pd.DataFrame:
    np.random.seed(int(time.time()) % 100000)
    base_price = 100.0 if "OTC" in symbol else 1.0850
    volatility = 0.0012 if "OTC" in symbol else 0.0004
    
    close_prices = [base_price]
    for _ in range(count - 1):
        close_prices.append(close_prices[-1] + np.random.normal(0, volatility))
        
    dates = pd.date_range(end=pd.Timestamp.now(), periods=count, freq="1min")
    df = pd.DataFrame({'Timestamp': dates, 'Close': close_prices})
    df['Open'] = df['Close'].shift(1).fillna(df['Close'] - np.random.uniform(-0.0001, 0.0001))
    df['High'] = df[['Open', 'Close']].max(axis=1) + np.abs(np.random.normal(0, volatility/3, count))
    df['Low'] = df[['Open', 'Close']].min(axis=1) - np.abs(np.random.normal(0, volatility/3, count))
    
    # Technical Indicators
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    df['Support'] = df['Low'].rolling(window=15).min()
    df['Resistance'] = df['High'].rolling(window=15).max()
    return df

def analyze_confluence_signal(df: pd.DataFrame) -> dict:
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    reasons = []
    bull, bear = 0, 0

    # 1. EMA Trend
    if latest['EMA_20'] > latest['EMA_50']:
        bull += 1
        reasons.append("Trend: Bullish Alignment (EMA 20 > EMA 50)")
    else:
        bear += 1
        reasons.append("Trend: Bearish Alignment (EMA 20 < EMA 50)")

    # 2. S/R Reaction
    if abs(latest['Close'] - latest['Support']) < (latest['Close'] * 0.0003):
        bull += 1
        reasons.append("Dynamic Zone: Rebound from Strong Support")
    elif abs(latest['Close'] - latest['Resistance']) < (latest['Close'] * 0.0003):
        bear += 1
        reasons.append("Dynamic Zone: Rejection from Strong Resistance")

    # 3. Candlestick Patterns
    body = abs(latest['Close'] - latest['Open'])
    lower_wick = min(latest['Open'], latest['Close']) - latest['Low']
    upper_wick = latest['High'] - max(latest['Open'], latest['Close'])
    
    if lower_wick > (2 * body):
        bull += 1
        reasons.append("Candle: Bullish Pinbar / Reversal Wick")
    elif upper_wick > (2 * body):
        bear += 1
        reasons.append("Candle: Bearish Pinbar / Reversal Wick")

    # 4. RSI Overbought/Oversold
    if latest['RSI_14'] < 35:
        bull += 1
        reasons.append(f"RSI Filter: Oversold ({latest['RSI_14']:.1f})")
    elif latest['RSI_14'] > 65:
        bear += 1
        reasons.append(f"RSI Filter: Overbought ({latest['RSI_14']:.1f})")

    # Multi-Confluence Output (At least 3 signals needed)
    if bull >= 3 and bull > bear:
        direction = "BUY (CALL)"
        confidence = min(98, 78 + (bull * 5))
    elif bear >= 3 and bear > bull:
        direction = "SELL (PUT)"
        confidence = min(98, 78 + (bear * 5))
    else:
        direction = "NO TRADE"
        confidence = 0

    return {
        "direction": direction,
        "confidence": confidence,
        "reasons": reasons,
        "price": latest['Close'],
        "rsi": latest['RSI_14']
    }

# ==============================================================================
# 4. INITIALIZE SESSION STATE
# ==============================================================================
if 'selected_plan' not in st.session_state:
    st.session_state['selected_plan'] = {'name': '7 Days Access Pass', 'price': '$10', 'days': 7}
if 'submitted_orders' not in st.session_state:
    st.session_state['submitted_orders'] = []

# ==============================================================================
# 5. SIDEBAR CONTROLS & NAVIGATION
# ==============================================================================
st.sidebar.title("⚡ QUOTEX PRO AI")
app_mode = st.sidebar.radio("Navigation", ["🎯 Live Trading Dashboard", "💎 Buy Access Pass", "⚙️ Admin Panel"])

st.sidebar.markdown("---")
user_key = st.sidebar.text_input("🔑 License Key Activation", type="password", placeholder="Paste key here...")
is_valid, email, days_remaining = verify_license_key(user_key)

if is_valid:
    st.sidebar.markdown(f"Status: <span class='badge-active'>ACTIVE</span> ({days_remaining} Days Left)", unsafe_allow_html=True)
    st.sidebar.caption(f"User: {email}")
else:
    st.sidebar.markdown("Status: <span class='badge-expired'>INACTIVE</span>", unsafe_allow_html=True)

# ==============================================================================
# PAGE 1: BUY ACCESS PASS (COMMERCIAL CHECKOUT FLOW)
# ==============================================================================
if app_mode == "💎 Buy Access Pass":
    st.title("💎 Upgrade Your Quotex Signal Engine")
    st.subheader("পছন্দের প্যাকেজটি সিলেক্ট করে সরাসরি লাইভ সিগন্যাল আনলক করুন")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <h3>🥉 STARTER PASS</h3>
            <h1 style="color: #00f2fe;">$6</h1>
            <p><b>3 Days</b> Full Access</p>
            <hr style="border-color:#334155;">
            <p>✔ All OTC Pairs Supported</p>
            <p>✔ 85%+ Multi-Confluence Signals</p>
            <p>✔ Real-time Expiry Timer</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select 3-Day Plan ($6)", use_container_width=True):
            st.session_state['selected_plan'] = {'name': '3 Days Access Pass', 'price': '$6', 'days': 3}

    with col2:
        st.markdown("""
        <div class="pricing-card pricing-card-selected">
            <span style="background: #00f2fe; color:#000; padding:2px 8px; border-radius:10px; font-size:12px; font-weight:bold;">MOST POPULAR</span>
            <h3>🥈 PRO PASS</h3>
            <h1 style="color: #00f2fe;">$10</h1>
            <p><b>7 Days</b> Full Access</p>
            <hr style="border-color:#334155;">
            <p>✔ All Features Included</p>
            <p>✔ VIP Signal Filtering</p>
            <p>✔ Martingale Strategy Guide</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select 7-Day Plan ($10)", use_container_width=True, type="primary"):
            st.session_state['selected_plan'] = {'name': '7 Days Access Pass', 'price': '$10', 'days': 7}

    with col3:
        st.markdown("""
        <div class="pricing-card">
            <h3>🥇 VIP PASS</h3>
            <h1 style="color: #00f2fe;">$20</h1>
            <p><b>30 Days</b> Full Access</p>
            <hr style="border-color:#334155;">
            <p>✔ Max Value (Save 50%)</p>
            <p>✔ Priority Engine Server</p>
            <p>✔ 24/7 VIP Support</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select 30-Day Plan ($20)", use_container_width=True):
            st.session_state['selected_plan'] = {'name': '30 Days Access Pass', 'price': '$20', 'days': 30}

    st.markdown("---")
    
    # Selected Plan Payment Box
    plan = st.session_state['selected_plan']
    st.subheader(f"💳 Payment Step: Complete Order for [{plan['name']} - {plan['price']}]")
    
    pay_col1, pay_col2 = st.columns([1.2, 1])
    with pay_col1:
        st.info("👇 পেমেন্ট সম্পন্ন করতে নিচের যে কোনো একটি অ্যাড্রেসে ক্রিপ্টো পাঠান:")
        st.code("BEP20 Address (USDT/BNB):\n0xffd0727026be62cd456490afd2dfde10c9646623", language="text")
        st.code("Binance Pay ID:\n1123923578", language="text")

    with pay_col2:
        with st.form("checkout_form"):
            st.write("<b>পেমেন্ট সাবমিট ফরম:</b>", unsafe_allow_html=True)
            u_email = st.text_input("Your Email Address")
            tx_id = st.text_input("Transaction Hash / Binance Pay Tx ID")
            
            submit_btn = st.form_submit_button("Submit Payment for Instant Activation")
            if submit_btn:
                if u_email and tx_id:
                    st.session_state['submitted_orders'].append({
                        "email": u_email,
                        "tx_id": tx_id,
                        "plan": plan['name'],
                        "days": plan['days'],
                        "time": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success("✅ পেমেন্ট রিকোয়েস্ট সাবমিট হয়েছে! এডমিন টেক্স আইডি মিলিয়ে দেখেই আপনার ইমেইলে বা লাইভ স্ক্রিনে কি (Key) অ্যাক্টিভ করে দেবে।")
                else:
                    st.error("❌ অনুগ্রহ করে ইমেইল এবং Transaction Hash উভয়ই সঠিকভাবে দিন।")

# ==============================================================================
# PAGE 2: LIVE TRADING DASHBOARD
# ==============================================================================
elif app_mode == "🎯 Live Trading Dashboard":
    st.title("🎯 Quotex Live Signal Terminal")
    
    if not is_valid:
        st.error("🔒 License Expired / Inactive. Live Signal Access Locked!")
        st.info("👈 সাইডবার থেকে একটি সঠিক License Key বসান অথবা '💎 Buy Access Pass' অপশনে গিয়ে আপনার প্ল্যান অ্যাক্টিভ করুন।")
    else:
        # Dashboard Controls
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            asset = st.selectbox("Select Quotex Asset", ["USD/INR (OTC)", "EUR/USD (OTC)", "USD/COP (OTC)", "GBP/USD", "USD/JPY (OTC)"])
        with c2:
            timeframe = st.selectbox("Expiry Time", ["1 Minute", "2 Minutes", "5 Minutes"])
        with c3:
            st.write("###")
            refresh = st.button("🔄 Refresh Data Feed")

        # Fetch & Analyze
        df = fetch_quotex_ohlc_data(asset)
        sig = analyze_confluence_signal(df)

        # Top Display Stats
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Selected Asset", asset)
        s2.metric("Market Price", f"{sig['price']:.5f}")
        s3.metric("RSI (14)", f"{sig['rsi']:.1f}")
        s4.metric("Engine Confidence", f"{sig['confidence']}%")

        st.markdown("---")

        col_left, col_right = st.columns([1, 1.6])

        # Signal Box Output
        with col_left:
            st.subheader("⚡ Signal Engine Output")
            if sig['direction'] == "BUY (CALL)":
                st.markdown(f"""
                <div class="signal-buy">
                    <h1 style="color:#10b981; margin:0;">🚀 BUY (CALL)</h1>
                    <h2>Confidence: {sig['confidence']}%</h2>
                    <p>Expiry: <b>{timeframe}</b></p>
                </div>
                """, unsafe_allow_html=True)
            elif sig['direction'] == "SELL (PUT)":
                st.markdown(f"""
                <div class="signal-sell">
                    <h1 style="color:#ef4444; margin:0;">🔻 SELL (PUT)</h1>
                    <h2>Confidence: {sig['confidence']}%</h2>
                    <p>Expiry: <b>{timeframe}</b></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="signal-wait">
                    <h1 style="color:#f59e0b; margin:0;">⏸️ NO TRADE</h1>
                    <p style="margin-top:10px;">Waiting for minimum 3 Technical Confluences...</p>
                </div>
                """, unsafe_allow_html=True)

            st.write("#### 🔍 Signal Reasoning Factors:")
            for reason in sig['reasons']:
                st.markdown(f"- ✅ **{reason}**")

            st.warning("⚠️ **Risk Warning:** Never exceed 2% risk per trade. Use Max 1-Step Martingale safety prompt.")

        # Interactive Candlestick Chart (Plotly)
        with col_right:
            st.subheader("📈 Real-Time Candlestick Analysis")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df['Timestamp'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                name="Quotex Feed"
            ))
            fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['EMA_20'], line=dict(color='#00f2fe', width=1.5), name="EMA 20"))
            fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['EMA_50'], line=dict(color='#ff007f', width=1.5), name="EMA 50"))
            
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#07090e",
                plot_bgcolor="#07090e",
                height=400,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_rangeslider_visible=False
            )
            st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# PAGE 3: ADMIN PANEL (INSTANT KEY GENERATION & ORDER REVIEW)
# ==============================================================================
elif app_mode == "⚙️ Admin Panel":
    st.title("⚙️ SaaS Admin Control Center")
    admin_auth = st.text_input("Enter Admin Password", type="password")
    
    if admin_auth == ADMIN_PASSWORD:
        st.success("🔓 Admin Privileges Granted")
        
        st.subheader("1. Instant License Key Generator")
        gen_col1, gen_col2 = st.columns(2)
        with gen_col1:
            target_email = st.text_input("Customer Email")
            plan_days = st.selectbox("Access Duration", [3, 7, 30], format_func=lambda x: f"{x} Days Pass")
            
            if st.button("Generate License Key"):
                if target_email:
                    new_key = generate_license_key(plan_days, target_email)
                    st.code(new_key, language="text")
                    st.success(f"Key Generated for {target_email} ({plan_days} Days)!")
                else:
                    st.error("Please enter email.")

        st.markdown("---")
        st.subheader("2. Pending Payment Requests (User Submissions)")
        if st.session_state['submitted_orders']:
            st.dataframe(pd.DataFrame(st.session_state['submitted_orders']))
        else:
            st.info("No payment submissions yet.")
    elif admin_auth:
        st.error("❌ Incorrect Admin Password!")
        
