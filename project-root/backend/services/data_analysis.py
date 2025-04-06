import yfinance as yf
import pandas
import torch

def fetch_data(ticker, period, interval):
    data = yf.download(tickers=ticker, period=period, interval=interval)

    dates = [date.strftime("%Y-%m-%d") for date in data.index]
    
    open = [round(x[0], 2) if isinstance(x, list) else round(x, 2) for x in data["Open"].values.tolist()]
    high = [round(x[0], 2) if isinstance(x, list) else round(x, 2) for x in data["High"].values.tolist()]
    low = [round(x[0], 2) if isinstance(x, list) else round(x, 2) for x in data["Low"].values.tolist()]
    close = [round(x[0], 2) if isinstance(x, list) else round(x, 2) for x in data["Close"].values.tolist()]
    volume = [x[0] if isinstance(x, list) else x for x in data["Volume"].values.tolist()]
        
    return [dates, open, high, low, close, volume]


def fetch_data_type(ticker, closing_price, period, interval):
    data = yf.download(tickers=ticker, period=period, interval=interval)

    if closing_price:
        price_type = 'Close'
    else:
        price_type = 'Open'

    result = data[[price_type]].rename(columns={price_type: 'Price'})

    dates = [date.strftime("%Y-%m-%d") for date in result.index]

    prices = data[price_type].values.tolist()
    prices = [round(item[0], 2) for item in data[price_type].values.tolist()]

    return [dates, prices]

#def calculate_stats(data_array):

