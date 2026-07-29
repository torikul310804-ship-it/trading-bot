import pandas as pd
import numpy as np
from typing import Dict, Any

class QuantitativeSignalEngine:
    def __init__(self, df_1m: pd.DataFrame, df_5m: pd.DataFrame):
        self.df_1m = df_1m.copy()
        self.df_5m = df_5m.copy()
        self._compute_indicators()

    def _compute_indicators(self):
        self.df_5m["EMA_20"] = self.df_5m["Close"].ewm(span=20, adjust=False).mean()
        self.df_5m["EMA_50"] = self.df_5m["Close"].ewm(span=50, adjust=False).mean()

        df = self.df_1m
        df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()

        df["SMA_20"] = df["Close"].rolling(20).mean()
        df["STD_20"] = df["Close"].rolling(20).std()
        df["BB_Upper"] = df["SMA_20"] + (df["STD_20"] * 2)
        df["BB_Lower"] = df["SMA_20"] - (df["STD_20"] * 2)
        df["BB_Bandwidth"] = (df["BB_Upper"] - df["BB_Lower"]) / df["SMA_20"]

        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-9)
        df["RSI"] = 100 - (100 / (1 + rs))

        ema_12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema_26 = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = ema_12 - ema_26
        df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
        df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

        self.df_1m = df

    def evaluate_market_safety(self) -> tuple[bool, str]:
        df = self.df_1m
        latest = df.iloc[-1]
        prev_bars = df.tail(10)

        bb_bandwidth = latest["BB_Bandwidth"]
        if bb_bandwidth < df["BB_Bandwidth"].quantile(0.20) or (prev_bars["High"].max() - prev_bars["Low"].min()) / latest["Close"] < 0.0005:
            return False, "NO TRADE - MARKET CONSOLIDATING / SIDEWAYS (Low Liquidity)"

        body = abs(latest["Close"] - latest["Open"])
        candle_range = latest["High"] - latest["Low"]
        wick_ratio = (candle_range - body) / candle_range if candle_range > 0 else 0

        if wick_ratio > 0.75 or candle_range > (df["High"] - df["Low"]).tail(20).mean() * 2.5:
            return False, "NO TRADE - HIGH ERRATIC VOLATILITY / FAKEOUT WICKS DETECTED"

        return True, "SAFE"

    def analyze_signal(self) -> Dict[str, Any]:
        is_safe, safety_msg = self.evaluate_market_safety()
        if not is_safe:
            return {
                "action": "⏸️ NO TRADE",
                "confidence": "0%",
                "status": safety_msg,
                "reasons": ["Market structure shows high risk of whipsaws or low breakout momentum."],
                "timeframe": "1 Minute Expiration",
                "risk_advice": "Do not enter position. Await market expansion or clean trend establishment."
            }

        df1 = self.df_1m
        df5 = self.df_5m
        curr1 = df1.iloc[-1]
        prev1 = df1.iloc[-2]
        curr5 = df5.iloc[-1]

        score_buy = 0
        score_sell = 0
        reasons = []

        if curr5["EMA_20"] > curr5["EMA_50"]:
            score_buy += 25
            reasons.append("5M Trend Alignment: Bullish (EMA 20 > EMA 50)")
        elif curr5["EMA_20"] < curr5["EMA_50"]:
            score_sell += 25
            reasons.append("5M Trend Alignment: Bearish (EMA 20 < EMA 50)")

        recent_low = df1["Low"].tail(20).min()
        recent_high = df1["High"].tail(20).max()
        near_support = abs(curr1["Close"] - recent_low) / curr1["Close"] < 0.0008
        near_resistance = abs(curr1["Close"] - recent_high) / curr1["Close"] < 0.0008

        if near_support:
            score_buy += 20
            reasons.append("Price Action: Retesting Key Demand Zone / Support Level")
        if near_resistance:
            score_sell += 20
            reasons.append("Price Action: Retesting Key Supply Zone / Resistance Level")

        body = curr1["Close"] - curr1["Open"]
        prev_body = prev1["Close"] - prev1["Open"]

        if prev_body < 0 and body > 0 and curr1["Close"] >= prev1["Open"] and curr1["Open"] <= prev1["Close"]:
            score_buy += 25
            reasons.append("Candlestick: Strong Bullish Engulfing Pattern Detected")
        elif prev_body > 0 and body < 0 and curr1["Close"] <= prev1["Open"] and curr1["Open"] >= prev1["Close"]:
            score_sell += 25
            reasons.append("Candlestick: Strong Bearish Engulfing Pattern Detected")

        lower_wick = min(curr1["Open"], curr1["Close"]) - curr1["Low"]
        upper_wick = curr1["High"] - max(curr1["Open"], curr1["Close"])
        total_len = curr1["High"] - curr1["Low"]

        if total_len > 0:
            if lower_wick / total_len > 0.6:
                score_buy += 20
                reasons.append("Candlestick: Bullish Pinbar / Rejection Wick at Support")
            elif upper_wick / total_len > 0.6:
                score_sell += 20
                reasons.append("Candlestick: Bearish Shooting Star / Rejection Wick at Resistance")

        if curr1["RSI"] < 35:
            score_buy += 15
            reasons.append(f"RSI Indicator: Oversold ({curr1['RSI']:.1f})")
        elif curr1["RSI"] > 65:
            score_sell += 15
            reasons.append(f"RSI Indicator: Overbought ({curr1['RSI']:.1f})")

        if curr1["MACD"] > curr1["MACD_Signal"] and prev1["MACD"] <= prev1["MACD_Signal"]:
            score_buy += 15
            reasons.append("MACD: Bullish Crossover Confluence")
        elif curr1["MACD"] < curr1["MACD_Signal"] and prev1["MACD"] >= prev1["MACD_Signal"]:
            score_sell += 15
            reasons.append("MACD: Bearish Crossover Confluence")

        if curr1["Close"] <= curr1["BB_Lower"]:
            score_buy += 10
            reasons.append("Bollinger Bands: Lower Band Breakout/Touch")
        elif curr1["Close"] >= curr1["BB_Upper"]:
            score_sell += 10
            reasons.append("Bollinger Bands: Upper Band Breakout/Touch")

        if score_buy >= 55 and score_buy > score_sell:
            confidence = min(score_buy, 96)
            return {
                "action": "🚀 BUY (CALL)",
                "confidence": f"{confidence}% Strong Alignment",
                "status": "VALID SIGNAL EXECUTION",
                "reasons": reasons,
                "timeframe": "1 Minute Expiration",
                "risk_advice": "Risk 1-2% Per Trade. If loss occurs, Max 1-Step Martingale on next candle only."
            }
        elif score_sell >= 55 and score_sell > score_buy:
            confidence = min(score_sell, 96)
            return {
                "action": "🔻 SELL (PUT)",
                "confidence": f"{confidence}% Strong Alignment",
                "status": "VALID SIGNAL EXECUTION",
                "reasons": reasons,
                "timeframe": "1 Minute Expiration",
                "risk_advice": "Risk 1-2% Per Trade. If loss occurs, Max 1-Step Martingale on next candle only."
            }
        else:
            return {
                "action": "⏸️ WAIT (NO TRADE)",
                "confidence": "Low Confluence (< 55%)",
                "status": "NO CLEAR SETUP",
                "reasons": ["Technical indicators are mixed or conflicting between 1M and 5M timeframes."],
                "timeframe": "1 Minute Expiration",
                "risk_advice": "Preserve capital. Wait for next candle close for confirmation."
      }
              
