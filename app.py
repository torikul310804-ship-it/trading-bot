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
# 1. PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="QUANTX GLOBAL | Trading Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Auto Refresh (Every 20 Seconds)
st_autorefresh(interval=20000, key="global_exchange_refresh")

# CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');

    :root {
        --bg-dark: #0e131f;
        --card-bg: rgba(24, 31, 46, 0.9);
        --accent-green: #00b964;
        --accent-red: #f23645;
        --text-primary: #ffffff;
        --text-secondary: #94a3b8;
    }

    body, .stApp {
        background-color: var(--bg-dark);
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: var(--text-primary);
    }

    header, footer { visibility: hidden; }
    .block-container { padding-top: 0.5rem; padding-bottom: 3rem; }

    /* Top Banner */
    .promo-banner {
        background: linear-gradient(90deg, #059669, #0d9488);
        padding: 8px 15px;
        border-radius: 8px;
        color: white;
        font-size: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }

    /* Glass Cards */
    .glass-card {
        background: var(--card-bg);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }

    .font-orbitron { font-family: 'Orbitron', sans-serif; }
    .text-green { color: var(--accent-green); }
    .text-red { color: var(--accent-red); }

    /* Custom Buttons */
    .stButton > button {
        border-radius: 8px;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        border: none;
        height: 45px;
    }

    .btn-up > button {
        background: #00b964 !important;
        color: white !important;
    }

    .btn-down > button {
        background: #f23645 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE MANAGEMENT
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = True

if "user" not in st.session_state:
    st.session_state.user = {
        "username": "TraderGlobal",
        "email": "torikul310861@gmail.com",
        "id": "91252094",
        "live_balance": 0.00,
        "demo_balance": 10000.00,
        "verified": False,
        "first_name": "",
        "last_name": "",
        "country": "Bangladesh"
    }

if "account_type" not in st.session_state:
    st.session_state.account_type = "DEMO"

if "trade_history" not in st.session_state:
    st.session_state.trade_history = []

# ==========================================
# 3. TOP NAVIGATION HEADER
# ==========================================
col_top1, col_top2 = st.columns([2, 1])

with col_top1:
    acc_type = st.session_state.account_type
    bal = st.session_state.user["demo_balance"] if acc_type == "DEMO" else st.session_state.user["live_balance"]
    
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px;">
        <div style="background:#181f2e; border:1px solid #334155; padding:6px 12px; border-radius:8px;">
            <span style="font-size:10px; font-weight:800; padding:2px 6px; border-radius:4px; background:{'rgba(245, 158, 11, 0.2)' if acc_type == 'DEMO' else 'rgba(0, 185, 100, 0.2)'}; color:{'#f59e0b' if acc_type == 'DEMO' else '#00b964'};">{acc_type}</span>
            <span class="font-orbitron" style="font-size:16px; font-weight:700; margin-left:8px;">${bal:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_top2:
    st.markdown("""
    <div style="text-align: right;">
        <button style="background:#00b964; color:white; border:none; padding:8px 20px; border-radius:6px; font-weight:bold; cursor:pointer;">
            Deposit
        </button>
    </div>
    """, unsafe_allow_html=True)

# Promo Banner
st.markdown("""
<div class="promo-banner">
    <span>🚀 Get a <b>50% bonus</b> on your deposit!</span>
    <span style="background:rgba(255,255,255,0.2); padding:2px 6px; border-radius:4px; font-weight:bold; font-size:10px;">50%</span>
</div>
""", unsafe_allow_html=True)

# Switch Account Type Toggle
selected_acc = st.radio("Account Type", ["DEMO ACCOUNT", "LIVE ACCOUNT"], horizontal=True, label_visibility="collapsed")
st.session_state.account_type = "DEMO" if "DEMO" in selected_acc else "LIVE"

# ==========================================
# 4. MAIN NAVIGATION TABS
# ==========================================
tab_trade, tab_profile, tab_more = st.tabs(["📈 Trades", "👤 Profile", "☰ More"])

# ------------------------------------------
# TAB 1: TRADING TERMINAL
# ------------------------------------------
with tab_trade:
    # Asset & Inputs
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        asset = st.selectbox("Select Pair", ["EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)"], label_visibility="collapsed")
    with c2:
        timer_val = st.text_input("Timer", value="00:01:00", label_visibility="collapsed")
    with c3:
        invest_amount = st.number_input("Investment ($)", min_value=1.0, value=1.0, step=1.0, label_visibility="collapsed")

    # Generate Dummy Chart
    dates = pd.date_range(end=pd.Timestamp.now(), periods=40, freq="1min")
    np.random.seed(42)
    prices = 1.15000 + np.cumsum(np.random.normal(0, 0.0001, 40))
    df = pd.DataFrame({
        "time": dates,
        "open": prices,
        "high": prices + 0.00008,
        "low": prices - 0.00008,
        "close": prices + np.random.normal(0, 0.00004, 40)
    })

    fig = go.Figure(data=[go.Candlestick(
        x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close']
    )])
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(14, 19, 31, 1)',
        height=320,
        margin=dict(l=5, r=5, t=5, b=5),
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)

    # Payout Info & Trading Buttons
    payout = invest_amount * 1.92
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; font-size:12px; color:#94a3b8; margin-bottom:8px;">
        <span>Payout Rate: <b style="color:#00b964;">92%</b></span>
        <span>Return: <b style="color:#00b964;" class="font-orbitron">${payout:.2f}</b></span>
    </div>
    """, unsafe_allow_html=True)

    btn1, btn2 = st.columns(2)
    with btn1:
        st.markdown("<div class='btn-up'>", unsafe_allow_html=True)
        if st.button("🟢 Up", use_container_width=True):
            win = random.choice([True, False])
            curr_acc = "demo_balance" if st.session_state.account_type == "DEMO" else "live_balance"
            if win:
                st.session_state.user[curr_acc] += (invest_amount * 0.92)
                st.success("Trade Won!")
            else:
                st.session_state.user[curr_acc] -= invest_amount
                st.error("Trade Lost!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with btn2:
        st.markdown("<div class='btn-down'>", unsafe_allow_html=True)
        if st.button("🔴 Down", use_container_width=True):
            win = random.choice([True, False])
            curr_acc = "demo_balance" if st.session_state.account_type == "DEMO" else "live_balance"
            if win:
                st.session_state.user[curr_acc] += (invest_amount * 0.92)
                st.success("Trade Won!")
            else:
                st.session_state.user[curr_acc] -= invest_amount
                st.error("Trade Lost!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 2: PROFILE & KYC
# ------------------------------------------
with tab_profile:
    st.markdown("### My account")
    
    st.markdown(f"""
    <div class="glass-card">
        <div style="font-size:14px; font-weight:bold;">{st.session_state.user['email']}</div>
        <div style="font-size:12px; color:#94a3b8;">ID: {st.session_state.user['id']}</div>
        <div style="margin-top:6px;">
            <span style="background:rgba(242, 54, 69, 0.2); color:#f23645; border:1px solid rgba(242, 54, 69, 0.4); padding:2px 8px; border-radius:4px; font-size:11px;">
                ⚠️ Not verified
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("profile_form"):
        st.text_input("First Name", value=st.session_state.user["first_name"])
        st.text_input("Last Name", value=st.session_state.user["last_name"])
        st.selectbox("Country", ["Bangladesh", "India", "Pakistan", "United States"])
        if st.form_submit_button("Save Changes", use_container_width=True):
            st.success("Profile updated successfully!")

# ------------------------------------------
# TAB 3: MORE MENU
# ------------------------------------------
with tab_more:
    st.markdown("""
    <div class="glass-card">
        <div style="padding:10px 0; border-bottom:1px solid #334155;">📊 Analytics</div>
        <div style="padding:10px 0; border-bottom:1px solid #334155;">🏆 TOP Traders</div>
        <div style="padding:10px 0; border-bottom:1px solid #334155;">📡 Signals</div>
        <div style="padding:10px 0; border-bottom:1px solid #334155;">📥 Deposit</div>
        <div style="padding:10px 0; border-bottom:1px solid #334155;">📤 Withdrawal</div>
        <div style="padding:10px 0;">⚙️ Settings</div>
    </div>
    """, unsafe_allow_html=True)
