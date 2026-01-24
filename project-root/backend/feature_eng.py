import numpy as np
import pandas as pd
from typing import Any


def compute_returns(prices: list[Any]) -> dict:
    prices = pd.Series(prices)
    return {
        "returns": prices.pct_change(),
        "log_returns": (prices / prices.shift(1)).apply(
            lambda value: pd.NA if pd.isna(value) else np.log(value)
        ),
    }


def rolling_stats(series: list[Any], window: int = 14) -> dict:
    series = pd.Series(series)
    return {
        "rolling_mean": series.rolling(window=window).mean(),
        "rolling_std": series.rolling(window=window).std(),
    }


def rsi(series: list[Any], window: int = 14) -> dict:
    series = pd.Series(series)
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    return {
        "rsi": 100 - (100 / (1 + rs)),
    }


def macd(series: list[Any], fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    series = pd.Series(series)
    fast_ema = series.ewm(span=fast, adjust=False).mean()
    slow_ema = series.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return {
        "macd": macd_line,
        "macd_signal": signal_line,
        "macd_hist": macd_line - signal_line,
    }


def atr(high: list[Any], low: list[Any], close: list[Any], window: int = 14) -> dict:
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    high_low = high - low
    high_close = (high - close.shift(1)).abs()
    low_close = (low - close.shift(1)).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return {
        "atr": true_range.rolling(window=window).mean(),
    }


def volume_features(volume: list[Any], window: int = 20) -> dict:
    volume = pd.Series(volume)
    return {
        "volume_mean": volume.rolling(window=window).mean(),
        "volume_std": volume.rolling(window=window).std(),
        "volume_change": volume.pct_change(),
    }


