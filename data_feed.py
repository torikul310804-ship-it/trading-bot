import time
import numpy as np
import pandas as pd
import yfinance as yf

TICKER_MAP = {
    "EUR/USD (Real)": "EURUSD=X",
    "EUR/GBP (Real)": "EURGBP=X",
    "GBP/USD (Real)": "GBPUSD=X",
    "USD/JPY (Real)": "JPY=X",
    "AUD/CAD (Real)": "AUDCAD=X",
    "Gold / XAU/USD (Real)": "GC=F",
    "EUR/USD (OTC)": "OTC_EURUSD",
    "EUR/GBP (OTC)": "OTC_EURGBP",
    "GBP/USD (OTC)": "OTC_GBPUSD",
    "USD/JPY (OTC)": "OTC_USDJPY",
    "AUD/CAD (OTC)": "OTC_AUDCAD",
    "USD/COP (OTC)": "OTC_USDCOP",
    "USD/BRL (OTC)": "OTC_USDBRL",
    "USD/INR (OTC)": "OTC_USDINR",
    "USD/PKR (OTC)": "OTC_USDPKR",
    "USD/BDT (OTC)": "OTC_USDBDT",
    "Gold / XAU/USD (OTC)": "OTC_XAUUSD",
}

def fetch_market_data(pair_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    ticker_symbol = TICKER_MAP.get(pair_name, "EURUSD=X")

    if "OTC" in pair_name:
        return _generate_otc_data(pair_name)

    try:
        df_1m = yf.download(tickers=ticker_symbol, period="1d", interval="1m", progress=False)
        if df_1m.empty:
            return _generate_otc_data(pair_name)

        if isinstance(df_1m.columns, pd.MultiIndex):
            df_1m.columns = df_1m.columns.get_level_values(0)

        df_1m = df_1m[["Open", "High", "Low", "Close", "Volume"]].dropna()

        df_5m = df_1m.resample('5min').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()

        return df_1m.tail(120), df_5m.tail(60)

    except Exception:
        return _generate_otc_data(pair_name)

def _generate_otc_data(pair_name: str, bars: int = 150) -> tuple[pd.DataFrame, pd.DataFrame]:
    np.random.seed(int(time.time() * 1000) % 100000)

    base_price = 1.0850 if "USD" in pair_name else 100.0
    if "XAU" in pair_name:
        base_price = 2350.0
    elif "INR" in pair_name or "BDT" in pair_name or "PKR" in pair_name:
        base_price = 85.0

    now = pd.Timestamp.now(tz="UTC")
    times_1m = [now - pd.Timedelta(minutes=i) for i in range(bars - 1, -1, -1)]

    returns = np.random.normal(loc=0.00002, scale=0.0008, size=bars)
    prices = base_price * np.exp(np.cumsum(returns))

    data_1m = []
    for i in range(bars):
        close_p = prices[i]
        volatility = close_p * np.random.uniform(0.0003, 0.0012)
        open_p = close_p + np.random.uniform(-volatility, volatility)
        high_p = max(open_p, close_p) + abs(np.random.uniform(0, volatility * 1.2))
        low_p = min(open_p, close_p) - abs(np.random.uniform(0, volatility * 1.2))
        volume = int(np.random.uniform(100, 5000))

        data_1m.append({
            "Datetime": times_1m[i],
            "Open": open_p,
            "High": high_p,
            "Low": low_p,
            "Close": close_p,
            "Volume": volume
        })

    df_1m = pd.DataFrame(data_1m).set_index("Datetime")

    df_5m = df_1m.resample('5min').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()

    return df_1m, df_5m
        
