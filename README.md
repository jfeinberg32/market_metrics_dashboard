# Markets Metric Dashboard

A one-page Streamlit dashboard that shows the day's market state: equities, rates, credit, and cross-asset metrics, with levels, recent changes, and how unusual each move was.

## What it shows

- **State strip**: VIX, HY OAS, 10Y yield, and the 10Y–2Y spread, with the 1-day change.
- **What moved**: the three series with the largest 1-day move relative to their recent volatility (z-score over the last 60 days).
- **Panels**: Equities, Rates, Credit, and Cross-asset. Each row has the level, 1D / 1W / YTD change, a 3-year percentile, and a 60-day sparkline. Yields and spreads change in bps; everything else in %. A series whose latest data is older than the dashboard date shows that date next to its name.
- **Data checks**: any warnings raised while pulling data, in a collapsible section at the bottom.

## Data sources

| Source | Series |
| --- | --- |
| [FRED](https://fred.stlouisfed.org/) | VIX, 2Y / 10Y / 10Y real yields, 10Y–2Y spread, HY / IG / CCC OAS, broad dollar index, WTI crude |
| [Yahoo Finance](https://finance.yahoo.com/) (via `yfinance`) | S&P 500, Nasdaq 100, Russell 2000, Dow, and the RSP/SPY equal-weight vs. cap-weight ratio |

Equity data drops today's bar until 4:30pm New York time, so the dashboard only shows completed closes.

## Files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit entry point. Loads the data (cached for 1 hour) and renders the page. |
| `get_metrics.py` | Pulls FRED and Yahoo Finance series and returns them as one tidy DataFrame (`date, section, metric, series_id, value, unit`). Run it directly to print the latest value of each metric. |
| `format_metrics.py` | Computes per-series summaries (changes, percentile, z-score, sparkline) and builds the Streamlit layout. |
| `requirements.txt` | Python dependencies. |
| `.env.example` | Template for the `FRED_API_KEY` environment variable. |

## Setup

1. Get a free FRED API key: https://fred.stlouisfed.org/docs/api/api_key.html
2. Install dependencies and add your key:

   ```bash
   pip install -r requirements.txt
   cp .env.example .env   # then set FRED_API_KEY in .env
   ```

3. Run the dashboard:

   ```bash
   streamlit run app.py
   ```

To check the data pull without the UI, run `python get_metrics.py`.

## Adding a metric

Add an entry to `FRED_SERIES`, `YF_SERIES`, or `YF_RATIOS` in `get_metrics.py` with its `section`, `metric` name, and `unit` (`pct`, `bps`, `usd`, `index`, or `ratio`). It will show up in the matching panel automatically.
