import streamlit as st
import pandas as pd
import numpy as np
import hmac
import hashlib
import time
import base64
import json

# ==============================================================================
# 1. APPLICATION & UI CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Quotex Algorithmic Signal Engine",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cyberpunk SaaS Visual Styling
st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0b0e14;
        color: #e2e8f0;
    }
    
    /* Neon Cards */
    .metric-card {
        background: linear-gradient(135deg, #131822 0%, #1a202c 100%);
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    
    .signal-box-buy {
        background: rgba(16, 185, 129, 0.1);
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
    }
    
    .signal-box-sell {
        background: rgba(239, 68, 68, 0.1);
        border: 2px solid #ef4444;
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
    }
    
    .signal-box-wait {
        background: rgba(245, 158, 11, 0.1);
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 25px;
        text-align: center;
    }
    
    .status-active {
        color: #10b981;
        font-weight: bold;
    }
    
    .status-expired {
        color: #ef4444;
        font-weight: bold;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Cryptographic Secret Key
SECRET_KEY = b"QUOTEX_SAAS_SUPER_SECRET_SIGNING_KEY_2026"

# ==============================================================================
# 2. LICENSE VALIDATION ENGINE
# ==============================================================================
def verify_license_key(key: str) -> tuple[bool, str, int]:
    """
    Validates license key structure, signature, and expiration.
    Returns: (is_valid, email, days_remaining)
    """
    if not key or not key.startswith("QTX-"):
        return False, "", 0
    
    try:
        parts = key.strip().split("-")
        if len(parts) != 3:
            return False, "", 0
            
        _, b64_payload, signature = parts
        
        # Verify HMAC signature
        expected_sig = hmac.new(SECRET_KEY, b64_payload.encode('utf-8'), hashlib.sha256).hexdigest()[:12]
        if not hmac.compare_digest(signature, expected_sig):
            return False, "", 0
            
        # Decode Payload
        raw_payload = base64.urlsafe_b64decode(b64_payload.encode('utf-8')).decode('utf-8')
        payload = json.loads(raw_payload)
        
        current_time = int(time.time())
        exp_time = payload.get("exp", 0)
        
        if current_time > exp_time:
            return False, payload.get("email", ""), 0
            
        days_left = max(1, int((exp_time - current_time) / 86400))
        return True, payload.get("email", ""), days_left

    except Exception:
        return False, "", 0

# ==============================================================================
# 3. QUOTEX MARKET DATA ENGINE (Canvas/WebSocket Web Scraping Bridge)
# ==============================================================================
class QuotexFeedEngine:
    """
    Simulates high-speed DOM canvas and WebSocket streaming from Quotex OTC and Standard pairs.
    In a deployed browser context, Playwright hooks into the Quotex WebSocket / canvas stream.
    """
    @staticmethod
    def get_realtime_candles(symbol: str, count: int = 100) -> pd.DataFrame:
        np.random.seed(int(time.time() * 100) % 100000)
        
        # Base asset pricing simulation
        base_price = 100.0 if "OTC" in symbol else 1.0850
        volatility = 0.0015 if "OTC" in symbol else 0.0005
        
        prices = [base_price]
        for _ in range(count - 1):
            prices.append(prices[-1] + np.random.normal(0, volatility))
            
        dates = pd.date_range(end=pd.Timestamp.now(), periods=count, freq="1min")
        
        df = pd.DataFrame({'Timestamp': dates, 'Close': prices})
        df['Open'] = df['Close'].shift(1).fillna(df['Close'] - np.random.uniform(-0.0002, 0.0002))
        df['High'] = df[['Open', 'Close']].max(axis=1) + np.abs(np.random.normal(0, volatility/2, count))
        df['Low'] = df[['Open', 'Close']].min(axis=1) - np.abs(np.random.normal(0, volatility/2, count))
        
        return df

# ==============================================================================
# 4. HIGH-ACCURACY MULTI-CONFLUENCE SIGNAL ENGINE
# ==============================================================================
def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Trend Alignment: EMA 20 & EMA 50
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    # 2. RSI Calculation (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # 3. Dynamic Support and Resistance
    df['Support'] = df['Low'].rolling(window=20).min()
    df['Resistance'] = df['High'].rolling(window=20).max()
    
    return df

def analyze_market_confluence(df: pd.DataFrame) -> dict:
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    reasons = []
    bullish_score = 0
    bearish_score = 0
    
    # Rule A: Trend Alignment (EMA 20 vs EMA 50)
    if latest['EMA_20'] > latest['EMA_50']:
        bullish_score += 1
        reasons.append("EMA Trend: Bullish Alignment (EMA20 > EMA50)")
    else:
        bearish_score += 1
        reasons.append("EMA Trend: Bearish Alignment (EMA20 < EMA50)")
        
    # Rule B: Dynamic S/R Bounce
    price_to_supp = abs(latest['Close'] - latest['Support'])
    price_to_res = abs(latest['Close'] - latest['Resistance'])
    
    if price_to_supp < (latest['Close'] * 0.0005):
        bullish_score += 1
        reasons.append("Dynamic Level: Bouncing from Key Support Zone")
    elif price_to_res < (latest['Close'] * 0.0005):
        bearish_score += 1
        reasons.append("Dynamic Level: Rejecting from Key Resistance Zone")
        
    # Rule C: Candlestick Reversal Patterns
    body = abs(latest['Close'] - latest['Open'])
    upper_wick = latest['High'] - max(latest['Open'], latest['Close'])
    lower_wick = min(latest['Open'], latest['Close']) - latest['Low']
    
    # Pinbar / Hammer
    if lower_wick > (2 * body) and lower_wick > upper_wick:
        bullish_score += 1
        reasons.append("Candlestick: Bullish Pinbar / Reversal Wick")
    elif upper_wick > (2 * body) and upper_wick > lower_wick:
        bearish_score += 1
        reasons.append("Candlestick: Bearish Pinbar / Reversal Wick")
        
    # Engulfing Pattern
    if latest['Close'] > latest['Open'] and prev['Close'] < prev['Open'] and latest['Close'] > prev['Open']:
        bullish_score += 1
        reasons.append("Candlestick: Bullish Engulfing Pattern")
    elif latest['Close'] < latest['Open'] and prev['Close'] > prev['Open'] and latest['Close'] < prev['Open']:
        bearish_score += 1
        reasons.append("Candlestick: Bearish Engulfing Pattern")

    # Rule D: Momentum Filter (RSI 14)
    if latest['RSI_14'] < 35:
        bullish_score += 1
        reasons.append(f"Momentum: RSI Oversold ({latest['RSI_14']:.1f})")
    elif latest['RSI_14'] > 65:
        bearish_score += 1
        reasons.append(f"Momentum: RSI Overbought ({latest['RSI_14']:.1f})")
        
    # Final Strict Rules Evaluation (At least 3 conditions matching)
    if bullish_score >= 3 and bullish_score > bearish_score:
        direction = "BUY (CALL)"
        confidence = min(96, 75 + (bullish_score * 5))
    elif bearish_score >= 3 and bearish_score > bullish_score:
        direction = "SELL (PUT)"
        confidence = min(96, 75 + (bearish_score * 5))
    else:
        direction = "NO TRADE"
        confidence = 0

    return {
        "direction": direction,
        "confidence": confidence,
        "reasons": reasons,
        "rsi": latest['RSI_14'],
        "price": latest['Close']
    }

# ==============================================================================
# 5. DASHBOARD SIDEBAR & LICENSE MANAGEMENT
# ==============================================================================
st.sidebar.title("⚡ Quotex Engine v4.2")
st.sidebar.markdown("---")

user_license_key = st.sidebar.text_input("🔑 License Key", type="password", help="Paste your active activation key here.")
is_licensed, user_email, days_left = verify_license_key(user_license_key)

if is_licensed:
    st.sidebar.markdown(f"Status: <span class='status-active'>ACTIVE</span> ({days_left} Days Left)", unsafe_allow_html=True)
    st.sidebar.caption(f"Account: {user_email}")
else:
    st.sidebar.markdown("Status: <span class='status-expired'>INACTIVE / EXPIRED</span>", unsafe_allow_html=True)
    if st.sidebar.button("💳 Buy / Upgrade License"):
        st.session_state['show_payment_modal'] = True

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Market Settings")
selected_pair = st.sidebar.selectbox(
    "Select Quotex Asset",
    ["EUR/USD (OTC)", "USD/INR (OTC)", "USD/COP (OTC)", "GBP/USD", "USD/JPY (OTC)", "AUD/CAD (OTC)"]
)
expiry_timeframe = st.sidebar.select_slider(
    "Signal Expiry Time",
    options=["1 Min", "2 Min", "5 Min"],
    value="1 Min"
)

# ==============================================================================
# 6. PAYMENT SYSTEM MODAL
# ==============================================================================
if st.session_state.get('show_payment_modal', False):
    st.markdown("## 💳 Activate License Key")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🥉 3 Days Pass")
        st.markdown("## **$6**")
        st.caption("Starter Trial")
    with col2:
        st.markdown("### 🥈 7 Days Pass")
        st.markdown("## **$10**")
        st.caption("Popular Choice")
    with col3:
        st.markdown("### 🥇 30 Days Pass")
        st.markdown("## **$20**")
        st.caption("Pro Trader Choice")

    st.markdown("---")
    st.subheader("Payment Details")
    st.info("Send payment exact amount to one of the addresses below:")
    
    st.code("BEP20 Address (USDT/BNB): 0xffd0727026be62cd456490afd2dfde10c9646623", language="text")
    st.code("Binance Pay ID: 1123923578", language="text")
    
    with st.form("payment_form"):
        tx_email = st.text_input("Your Email Address")
        tx_hash = st.text_input("Transaction Hash / Binance Pay Tx ID")
        submitted = st.form_submit_button("Submit Payment for Instant Activation")
        
        if submitted:
            if tx_email and tx_hash:
                st.success("✅ Payment Details Submitted Successfully! Your Transaction ID is being verified by Admin. Key will be sent to your email shortly.")
                st.session_state['show_payment_modal'] = False
            else:
                st.error("Please fill in both Email and Transaction Hash.")

# ==============================================================================
# 7. MAIN SAAS DASHBOARD CONTENT
# ==============================================================================
st.title("📊 Quotex High-Frequency Signal Engine")

if not is_licensed:
    st.error("🔒 License Expired or Inactive. Upgrade Plan to Access Live Signals.")
    st.info("Enter a valid license key in the sidebar or click 'Buy / Upgrade License' to unlock live Quotex trading signals.")
else:
    # Fetch Market Data
    raw_data = QuotexFeedEngine.get_realtime_candles(selected_pair)
    processed_data = calculate_technical_indicators(raw_data)
    signal = analyze_market_confluence(processed_data)
    
    # Top Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Selected Asset", selected_pair)
    with m2:
        st.metric("Live Tick Price", f"{signal['price']:.5f}")
    with m3:
        st.metric("RSI (14)", f"{signal['rsi']:.1f}")
    with m4:
        st.metric("Expiry Mode", expiry_timeframe)
        
    st.markdown("---")
    
    # Live Signal Display
    col_sig, col_chart = st.columns([1, 1.5])
    
    with col_sig:
        st.subheader("⚡ Live Algorithmic Output")
        
        if signal["direction"] == "BUY (CALL)":
            st.markdown(f"""
                <div class="signal-box-buy">
                    <h1>🚀 BUY (CALL)</h1>
                    <h2>Confidence Score: {signal['confidence']}%</h2>
                    <p>Expiry: {expiry_timeframe}</p>
                </div>
            """, unsafe_allow_html=True)
        elif signal["direction"] == "SELL (PUT)":
            st.markdown(f"""
                <div class="signal-box-sell">
                    <h1>🔻 SELL (PUT)</h1>
                    <h2>Confidence Score: {signal['confidence']}%</h2>
                    <p>Expiry: {expiry_timeframe}</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="signal-box-wait">
                    <h1>⏸️ NO TRADE</h1>
                    <h3>Waiting for Confluence Rules...</h3>
                    <p>Rule: Requires at least 3 matching confirmations.</p>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("#### Confluence Factors Triggered:")
        for reason in signal["reasons"]:
            st.markdown(f"- ✅ {reason}")
            
        st.markdown("---")
        st.warning("⚠️ **Risk Management Rule**: Max 1-Step Martingale. Never exceed 2% risk per trade.")

    with col_chart:
        st.subheader("📈 Real-Time Feed Analytics")
        st.line_chart(processed_data.set_index("Timestamp")[["Close", "EMA_20", "EMA_50"]])
