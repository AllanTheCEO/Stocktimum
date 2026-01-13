from datetime import datetime, timedelta

import pandas
import yfinance as yf

import cache


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


def parse_interval(interval: str) -> tuple[int, str]:
    if not interval:
        return 1, "d"
    normalized = interval.strip().lower()
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
    return amount, suffix or "d"


def timestamp_format(interval: str) -> str:
    _, unit = parse_interval(interval)
    if unit in {"m", "h"}:
        return "%Y-%m-%d %H:%M"
    return "%Y-%m-%d"


def interval_step(interval: str) -> timedelta:
    amount, unit = parse_interval(interval)
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


def merge_data(existing: dict | None, incoming: dict | None) -> dict:
    if not existing and incoming:
        return incoming
    if existing and not incoming:
        return existing
    if not existing and not incoming:
        return {"dates": [], "open": [], "high": [], "low": [], "close": [], "volume": []}

    combined = {}
    for idx, date_value in enumerate(existing["dates"]):
        combined[date_value] = (
            existing["open"][idx],
            existing["high"][idx],
            existing["low"][idx],
            existing["close"][idx],
            existing["volume"][idx],
        )
    for idx, date_value in enumerate(incoming["dates"]):
        combined[date_value] = (
            incoming["open"][idx],
            incoming["high"][idx],
            incoming["low"][idx],
            incoming["close"][idx],
            incoming["volume"][idx],
        )

    ordered_dates = sorted(combined.keys())
    merged = {"dates": [], "open": [], "high": [], "low": [], "close": [], "volume": []}
    for date_value in ordered_dates:
        open_value, high_value, low_value, close_value, volume_value = combined[date_value]
        merged["dates"].append(date_value)
        merged["open"].append(open_value)
        merged["high"].append(high_value)
        merged["low"].append(low_value)
        merged["close"].append(close_value)
        merged["volume"].append(volume_value)
    return merged


def slice_data_range(data: dict, start: datetime | None, end: datetime | None, interval: str) -> dict:
    if not start and not end:
        return data
    date_format = timestamp_format(interval)
    sliced = {"dates": [], "open": [], "high": [], "low": [], "close": [], "volume": []}
    for idx, date_value in enumerate(data["dates"]):
        parsed_date = datetime.strptime(date_value, date_format)
        if start and parsed_date < start:
            continue
        if end and parsed_date > end:
            continue
        sliced["dates"].append(date_value)
        sliced["open"].append(data["open"][idx])
        sliced["high"].append(data["high"][idx])
        sliced["low"].append(data["low"][idx])
        sliced["close"].append(data["close"][idx])
        sliced["volume"].append(data["volume"][idx])
    return sliced


def cache_date_range(data: dict, interval: str) -> tuple[datetime | None, datetime | None]:
    if not data or not data.get("dates"):
        return None, None
    date_format = timestamp_format(interval)
    start_date = datetime.strptime(data["dates"][0], date_format)
    end_date = datetime.strptime(data["dates"][-1], date_format)
    return start_date, end_date


def fetch_full_data(ticker: str, period: str, interval: str, force: bool = False):
    symbol = normalize_symbol(ticker)
    cached_payload = None
    if not force:
        cached_payload = cache.load_cached_payload(symbol, interval)

    cached_data = cached_payload.get("data") if cached_payload else None
    desired_start = parse_period_start(period)
    desired_end = datetime.now()

    cache_start, cache_end = cache_date_range(cached_data, interval) if cached_data else (None, None)
    if cached_data and desired_start and cache_start and desired_start >= cache_start and cache_end:
        if desired_end <= cache_end:
            return slice_data_range(cached_data, desired_start, desired_end, interval)

    missing_data = None
    if cached_data and desired_start and cache_start and desired_start < cache_start:
        end_date = cache_start
        start_date = desired_start
        date_format = timestamp_format(interval)
        frame = yf.download(
            tickers=symbol,
            start=start_date.strftime(date_format),
            end=end_date.strftime(date_format),
            interval=interval,
            group_by="column",
        )
        frame = select_single_ticker_frame(frame, symbol)
        if not frame.empty:
            missing_data = merge_data(missing_data, frame_to_data(frame, interval))

    if cached_data and cache_end and desired_end > cache_end:
        date_format = timestamp_format(interval)
        start_date = cache_end + interval_step(interval)
        frame = yf.download(
            tickers=symbol,
            start=start_date.strftime(date_format),
            end=desired_end.strftime(date_format),
            interval=interval,
            group_by="column",
        )
        frame = select_single_ticker_frame(frame, symbol)
        if not frame.empty:
            missing_data = merge_data(missing_data, frame_to_data(frame, interval))

    if not cached_data:
        if desired_start:
            date_format = timestamp_format(interval)
            frame = yf.download(
                tickers=symbol,
                start=desired_start.strftime(date_format),
                end=desired_end.strftime(date_format),
                interval=interval,
                group_by="column",
            )
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

    combined_data = merge_data(cached_data, missing_data)
    cache.save_cached_payload(symbol, interval, combined_data)
    return slice_data_range(combined_data, desired_start, desired_end, interval)

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
