import os
from zoneinfo import ZoneInfo

import yfinance as yf
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from fredapi import Fred
from datetime import date, datetime, timedelta

load_dotenv()

prices = yf.download(['^IXIC','^GSPC','^DJI','^RUT','RSP'], interval='1d', start=date(date.today().year, 1, 1), auto_adjust=True)['Close']

rets = prices.pct_change().dropna()

FRED_API_KEY = os.getenv("FRED_API_KEY")
if not FRED_API_KEY:
    raise RuntimeError("FRED_API_KEY is not set. Copy .env.example to .env and add your key.")

fred = Fred(api_key=FRED_API_KEY)

FRED_SERIES = {
    "VIXCLS":       {"section": "volatility",  "metric": "VIX",                "unit": "index", "scale": 1},
    "DGS2":         {"section": "rates",       "metric": "2Y yield",           "unit": "pct",   "scale": 1},
    "DGS10":        {"section": "rates",       "metric": "10Y yield",          "unit": "pct",   "scale": 1},
    "DFII10":       {"section": "rates",       "metric": "10Y real yield",     "unit": "pct",   "scale": 1},
    "T10Y2Y":       {"section": "rates",       "metric": "10Y–2Y spread",      "unit": "bps",   "scale": 100},
    "BAMLH0A0HYM2": {"section": "credit",      "metric": "HY OAS",             "unit": "bps",   "scale": 100},
    "BAMLC0A0CM":   {"section": "credit",      "metric": "IG OAS",             "unit": "bps",   "scale": 100},
    "BAMLH0A3HYC":  {"section": "credit",      "metric": "CCC OAS",            "unit": "bps",   "scale": 100},
    "DTWEXBGS":     {"section": "cross_asset", "metric": "Broad dollar index", "unit": "index", "scale": 1},
    "DCOILWTICO":   {"section": "cross_asset", "metric": "WTI crude",          "unit": "usd",   "scale": 1},
}

YF_SERIES = {
    "^SPX": {"section": "equities", "metric": "S&P 500",      "unit": "index"},
    "^NDX": {"section": "equities", "metric": "Nasdaq",       "unit": "index"},
    "^RUT":  {"section": "equities", "metric": "Russell 2000", "unit": "index"},
    "^DJI": {"section": "equities", "metric": "Dow", "unit": "index"},
}
 
# Derived ratios: (numerator, denominator) -> metadata.
YF_RATIOS = {
    ("RSP", "SPY"): {"section": "equities", "metric": "Equal-weight / cap-weight", "unit": "ratio"},
}

def _tidy(s: pd.Series, series_id: str, meta: dict) -> pd.DataFrame:
    s = s.dropna()
    return pd.DataFrame(
        {
            "date": s.index,
            "section": meta["section"],
            "metric": meta["metric"],
            "series_id": series_id,
            "value": s.values.round(4),
            "unit": meta["unit"],
        }
    )

def _drop_incomplete_bar(closes: pd.DataFrame) -> pd.DataFrame:
    now_ny = datetime.now(ZoneInfo("America/New_York"))
    market_closed = now_ny.hour > 16 or (now_ny.hour == 16 and now_ny.minute >= 30)
    if not market_closed:
        closes = closes[closes.index.date < now_ny.date()]
    return closes

def fetch_equity_tidy(years: int = 3) -> pd.DataFrame:
    ratio_tickers = {t for pair in YF_RATIOS for t in pair}
    tickers = sorted(set(YF_SERIES) | ratio_tickers)
    start = date.today() - timedelta(days=365 * years)
 
    raw = yf.download(
        tickers,
        start=start,
        auto_adjust=True,   
        progress=False,
    )
    closes = raw["Close"] 
    if closes.index.tz is not None:
        closes.index = closes.index.tz_localize(None)
    closes.index = pd.to_datetime(closes.index).normalize()
    closes = _drop_incomplete_bar(closes)
 
    frames = []
    for ticker, meta in YF_SERIES.items():
        frames.append(_tidy(closes[ticker], ticker, meta))
 
    for (num, den), meta in YF_RATIOS.items():
        pair = closes[[num, den]].dropna()  # only dates where both traded
        frames.append(_tidy(pair[num] / pair[den], f"{num}/{den}", meta))
 
    return pd.concat(frames, ignore_index=True)

def fetch_fred_tidy(fred: Fred) -> pd.DataFrame:
    frames = []
    for series_id, meta in FRED_SERIES.items():
        s = fred.get_series(series_id, observation_start='2020-01-01')
        
        s = s.dropna()
    
        frames.append(
            pd.DataFrame(
                {
                    "date": pd.to_datetime(s.index),
                    "section": meta["section"],
                    "metric": meta["metric"],
                    "series_id": series_id,
                    "value": (s.values * meta["scale"]).round(4),
                    "unit": meta["unit"],
                }
            )
        )
    df = pd.concat(frames, ignore_index=True)
    df = df.astype({"section": "category", "unit": "category", "value": "float64"})
    df = df.sort_values(["section", "metric", "date"]).reset_index(drop=True)

    return df

def get_metrics(years: int = 3) -> pd.DataFrame:
    df = pd.concat([fetch_fred_tidy(fred), fetch_equity_tidy()], ignore_index=True)

    df = df.astype({"section": "category", "unit": "category", "value": "float64"})
    df = df.sort_values(["section", "metric", "date"]).reset_index(drop=True)
 
    return df

if __name__ == "__main__":
    df = pd.concat([fetch_fred_tidy(fred), fetch_equity_tidy()])
    print(df.groupby("metric", observed=True).tail(1).to_string(index=False))