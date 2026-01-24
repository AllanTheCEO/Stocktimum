from datetime import datetime, timedelta

import pandas
import yfinance as yf

import cache


cache_data_dir = str(cache.cache_db_path())

def normalize_tickers(ticker):
    if isinstance(ticker, (list, tuple)):
        normalized = [str(item).strip().upper() for item in ticker if str(item).strip()]
        return normalized
    return str(ticker).strip().upper()


def normalize_symbol(ticker: str) -> str:
    normalized = normalize_tickers(ticker)
    if isinstance(normalized, (list, tuple)):
        return normalized[0] if normalized else ""
    return normalized


def round_series(series: list[object], digits = 2):
    return [round(value, digits) if value is not None else None for value in series]


def select_single_ticker_frame(data, tickers):
    if isinstance(data.columns, pandas.MultiIndex):
        if isinstance(tickers, (list, tuple)) and tickers:
            return data.xs(tickers[0], level=1, axis=1)
        return data.xs(data.columns.levels[1][0], level=1, axis=1)
    return data


def parse_period_start(period: str) -> datetime | None:
    if not period:
        return None
    normalized = period.strip().lower()
    if normalized == "max":
        return None
    value = ""
    suffix = ""
    for char in normalized:
        if char.isdigit():
            value += char
        else:
            suffix += char
    if not value or not suffix:
        return None
    try:
        amount = int(value)
    except ValueError:
        return None
    unit_days = {
        "d": 1,
        "wk": 7,
        "mo": 30,
        "y": 365,
    }
    if suffix in unit_days:
        return datetime.now() - timedelta(days=amount * unit_days[suffix])
    if suffix == "h":
        return datetime.now() - timedelta(hours=amount)
    if suffix == "m":
        return datetime.now() - timedelta(minutes=amount)
    return None


def timestamp_format(interval: str) -> str:
    if interval and interval.strip().lower().endswith(("m", "h")):
        return "%Y-%m-%d %H:%M"
    return "%Y-%m-%d"


def frame_to_data(frame, interval: str) -> dict:
    date_format = timestamp_format(interval)
    dates = [date_value.strftime(date_format) for date_value in frame.index]
    return {
        "dates": dates,
        "open": round_series(frame["Open"].tolist()),
        "high": round_series(frame["High"].tolist()),
        "low": round_series(frame["Low"].tolist()),
        "close": round_series(frame["Close"].tolist()),
        "volume": [value if value is not None else None for value in frame["Volume"].tolist()],
    }


def interval_step(interval: str) -> timedelta:
    normalized = interval.strip().lower() if interval else "1d"
    value = ""
    suffix = ""
    for char in normalized:
        if char.isdigit():
            value += char
        else:
            suffix += char
    try:
        amount = int(value) if value else 1
    except ValueError:
        amount = 1
    unit = suffix or "d"
    if unit == "m":
        return timedelta(minutes=amount)
    if unit == "h":
        return timedelta(hours=amount)
    if unit == "wk":
        return timedelta(weeks=amount)
    if unit == "mo":
        return timedelta(days=30 * amount)
    if unit == "y":
        return timedelta(days=365 * amount)
    return timedelta(days=amount)

def parse_timestamp(value: str) -> datetime:
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported timestamp format: {value}")

def cache_date_range(data: dict, interval: str) -> tuple[datetime | None, datetime | None]:
    if not data or not data.get("dates"):
        return None, None

    start_date = parse_timestamp(data["dates"][0])
    end_date = parse_timestamp(data["dates"][-1])
    return start_date, end_date


def fetch_full_data(ticker: str, period: str, interval: str, force: bool = False):
    symbol = normalize_symbol(ticker)
    cached_payload = None if force else cache.load_cached_payload(symbol, interval)
    cached_data = cached_payload.get("data") if cached_payload else None
    desired_start = parse_period_start(period)
    desired_end = datetime.now()

    cache_start, cache_end = cache_date_range(cached_data, interval) if cached_data else (None, None)
    if cached_data and desired_start and cache_start and cache_end:
        if desired_start >= cache_start and desired_end <= cache_end:
            return cached_data

    def fetch_range(start: datetime, end: datetime) -> dict:
        frame = yf.download(
            tickers=symbol,
            start=start,
            end=end,
            interval=interval,
            group_by="column",
        )
        frame = select_single_ticker_frame(frame, symbol)
        if frame.empty:
            return {"dates": [], "open": [], "high": [], "low": [], "close": [], "volume": []}
        return frame_to_data(frame, interval)

    if cached_data and desired_start and cache_start and cache_end:
        if desired_start < cache_start and desired_end <= cache_end:
            missing_data = fetch_range(desired_start, cache_start)
            cached_data = {
                "dates": missing_data["dates"] + cached_data["dates"],
                "open": missing_data["open"] + cached_data["open"],
                "high": missing_data["high"] + cached_data["high"],
                "low": missing_data["low"] + cached_data["low"],
                "close": missing_data["close"] + cached_data["close"],
                "volume": missing_data["volume"] + cached_data["volume"],
            }
        elif desired_end > cache_end and desired_start >= cache_start:
            start_date = cache_end + interval_step(interval)
            missing_data = fetch_range(start_date, desired_end)
            cached_data = {
                "dates": cached_data["dates"] + missing_data["dates"],
                "open": cached_data["open"] + missing_data["open"],
                "high": cached_data["high"] + missing_data["high"],
                "low": cached_data["low"] + missing_data["low"],
                "close": cached_data["close"] + missing_data["close"],
                "volume": cached_data["volume"] + missing_data["volume"],
            }
        elif desired_start < cache_start and desired_end > cache_end:
            cached_data = fetch_range(desired_start, desired_end)
            cache.save_cached_payload(symbol, interval, cached_data)
            return cached_data
    if not cached_data:
        if desired_start:
            cached_data = fetch_range(desired_start, desired_end)
        else:
            frame = yf.download(tickers=symbol, period=period, interval=interval, group_by="column")
            frame = select_single_ticker_frame(frame, symbol)
            cached_data = frame_to_data(frame, interval) if not frame.empty else {
                "dates": [],
                "open": [],
                "high": [],
                "low": [],
                "close": [],
                "volume": [],
            }

    cache.save_cached_payload(symbol, interval, cached_data)
    return cached_data

def fetch_data(ticker: str, period: str, interval: str, force: bool = False):
    data = fetch_full_data(ticker, period, interval, force=force)
    return [
        data["dates"],
        data["open"],
        data["high"],
        data["low"],
        data["close"],
        data["volume"],
    ]


def fetch_data_type(ticker, closing_price, period, interval, force: bool = False):
    data = fetch_full_data(ticker, period, interval, force=force)

    if closing_price:
        price_type = 'Close'
    else:
        price_type = 'Open'

    dates = data["dates"]
    prices = data["close"] if price_type == "Close" else data["open"]

    return [dates, prices]

# def calculate_stats(data_array):
