import yfinance as yf
import pandas
import torch

def fetch_data(ticker, period, interval):
    data = yf.download(tickers=ticker, period=period, interval=interval)

    
    return data

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