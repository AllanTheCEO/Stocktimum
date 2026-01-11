import yfinance as yf
import pandas

def normalize_tickers(ticker):
    if isinstance(ticker, (list, tuple)):
        normalized = [str(item).strip().upper() for item in ticker if str(item).strip()]
        return normalized
    return str(ticker).strip().upper()

def round_series(series: list[object], digits = 2):
    return [round(value, digits) if value is not None else None for value in series]

def select_single_ticker_frame(data, tickers):
    if isinstance(data.columns, pandas.MultiIndex):
        if isinstance(tickers, (list, tuple)) and tickers:
            return data.xs(tickers[0], level=1, axis=1)
        return data.xs(data.columns.levels[1][0], level=1, axis=1)
    return data


def fetch_data(ticker: str, period, interval):
    ticker = ticker.strip().upper()
    normalized_ticker = normalize_tickers(ticker)
    data = yf.download(tickers=ticker, period=period, interval=interval, group_by="column")

    data = select_single_ticker_frame(data, normalized_ticker)
    dates = [date.strftime("%Y-%m-%d") for date in data.index]
    
    open = round_series(data["Open"].tolist())
    high = round_series(data["High"].tolist())
    low = round_series(data["Low"].tolist())
    close = round_series(data["Close"].tolist())
    volume = [value if value is not None else None for value in data["Volume"].tolist()]
        
    return [dates, open, high, low, close, volume]


def fetch_data_type(ticker, closing_price, period, interval):
    ticker = ticker.strip().upper() 
    normalized_ticker = normalize_tickers(ticker)
    data = yf.download(tickers=ticker, period=period, interval=interval)

    if closing_price:
        price_type = 'Close'
    else:
        price_type = 'Open'

    data = select_single_ticker_frame(data, normalized_ticker)
    dates = [date.strftime("%Y-%m-%d") for date in data.index]
    prices = round_series(data[price_type].tolist())

    return [dates, prices]

# def calculate_stats(data_array):

