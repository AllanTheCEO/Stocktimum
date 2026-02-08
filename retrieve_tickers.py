import pandas as pd
from pathlib import Path

OUT = Path("ticker_list.txt")

# ---- Sources (no Wikipedia / no iShares scraping) ----
SP500_URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
RUS1000_URL = "https://raw.githubusercontent.com/mcprentiss/Russell_1000_download/master/rus1000.csv"
NASDAQ100_URL = "https://yfiua.github.io/index-constituents/constituents-nasdaq100.csv"
DOW30_URL = "https://yfiua.github.io/index-constituents/constituents-dowjones.csv"

def normalize(series: pd.Series) -> list[str]:
    s = (
        series.astype(str)
        .str.strip()
        .str.upper()
        .str.replace(".", "-", regex=False)   # BRK.B -> BRK-B for Yahoo/yfinance
    )
    bad = {"", "NAN", "SYMBOL", "TICKER"}
    return [t for t in s.tolist() if t and t not in bad and "<" not in t and ">" not in t]

def pick_symbol_col(df: pd.DataFrame) -> pd.Series:
    for key in ("symbol", "ticker"):
        cols = [c for c in df.columns if key in str(c).lower()]
        if cols:
            return df[cols[0]]
    return df.iloc[:, 0]

# ---- Equity universes ----
sp500 = normalize(pd.read_csv(SP500_URL)["Symbol"])

rus1000 = pd.read_csv(RUS1000_URL, header=None).iloc[:, 0]
rus1000 = normalize(rus1000)

nasdaq100 = normalize(pick_symbol_col(pd.read_csv(NASDAQ100_URL)))
dow30 = normalize(pick_symbol_col(pd.read_csv(DOW30_URL)))

# ---- Common ETF groups (hardcoded) ----
etfs = [
    # broad benchmarks
    "SPY","VOO","IVV","VTI","ITOT","IWB","IWM","QQQ","DIA",
    # sector SPDRs
    "XLC","XLB","XLE","XLF","XLI","XLK","XLP","XLRE","XLU","XLV","XLY",
    # style/factor
    "IWF","IWD","MTUM","USMV","QUAL","VBR",
    # international
    "VXUS","VEA","VWO",
    # bonds/rates
    "BND","AGG","TLT","IEF","SHY",
]

all_tickers = sp500 + rus1000 + nasdaq100 + dow30 + [t.upper() for t in etfs]
all_tickers = sorted(set(all_tickers))
all_tickers = [f'"{ticker}"' for ticker in all_tickers]

OUT.write_text(",\n".join(all_tickers) + "\n", encoding="utf-8")
print("wrote", len(all_tickers), "tickers ->", OUT.resolve())
