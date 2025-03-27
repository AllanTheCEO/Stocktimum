import yfinance as yf
import pandas
import torch

def fetch_data(ticker, period, interval):
    data = yf.download(tickers=ticker, period=period, interval=interval)

    ''' dates = [date.strftime("%Y-%m-%d") for date in result.index]
    
    return data'''

    dates = [date.strftime("%Y-%m-%d") for date in data.index]
    
    open= data["Open"].values.tolist()
    high= data["High"].values.tolist()
    low= data["Low"].values.tolist()
    close= data["Close"].values.tolist()
    volume= data["Volume"].values.tolist()
        
    
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