import sys
import os
from services import data_analysis
import yfinance as yf

sys.path.append("/..")

def main():
    print(data_analysis.fetch_data_type(["AAPL"], True, "1wk", "1d"))

if __name__ == "__main__":
    main()