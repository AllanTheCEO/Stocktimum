import sys
import os
import data_analysis
import yfinance as yf

sys.path.append("/..")

def main():
    print(data_analysis.fetch_data("AAPL", "1mo", "1h"))

if __name__ == "__main__":
    main()