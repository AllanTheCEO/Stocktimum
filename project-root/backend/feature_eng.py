import numpy as np
import pandas as pd


FEATURE_VERSION = "v0.1"


def compute_returns(prices: pd.Series) -> dict:
    return {
        "version": FEATURE_VERSION,
        "returns": prices.pct_change(),
        "log_returns": (prices / prices.shift(1)).apply(
            lambda value: pd.NA if pd.isna(value) else np.log(value)
        ),
    }


def rolling_stats(series: pd.Series, window: int = 14) -> dict:
    return {
        "version": FEATURE_VERSION,
        "rolling_mean": series.rolling(window=window).mean(),
        "rolling_std": series.rolling(window=window).std(),
    }


def rsi(series: pd.Series, window: int = 14) -> dict:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    return {
        "version": FEATURE_VERSION,
        "rsi": 100 - (100 / (1 + rs)),
    }


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    fast_ema = series.ewm(span=fast, adjust=False).mean()
    slow_ema = series.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return {
        "version": FEATURE_VERSION,
        "macd": macd_line,
        "macd_signal": signal_line,
        "macd_hist": macd_line - signal_line,
    }


def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> dict:
    high_low = high - low
    high_close = (high - close.shift(1)).abs()
    low_close = (low - close.shift(1)).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return {
        "version": FEATURE_VERSION,
        "atr": true_range.rolling(window=window).mean(),
    }


def volume_features(volume: pd.Series, window: int = 20) -> dict:
    return {
        "version": FEATURE_VERSION,
        "volume_mean": volume.rolling(window=window).mean(),
        "volume_std": volume.rolling(window=window).std(),
        "volume_change": volume.pct_change(),
    }
