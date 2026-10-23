
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

PANELS = [  
    ("equities", "Equities"),
    ("rates", "Rates"),
    ("credit", "Credit"),
    ("cross_asset", "Cross-asset"),
]

STATE_STRIP = [
    ("VIXCLS", "VIX", "inverse"),
    ("BAMLH0A0HYM2", "HY OAS", "inverse"),
    ("DGS10", "10Y yield", "off"),
    ("T10Y2Y", "10Y–2Y", "off"),
]

Z_WINDOW = 60      
SPARK_WINDOW = 60 


# ---------------------------------------------------------------- calculations

def _fmt_level(v: float, unit: str) -> str:
    return {
        "pct": f"{v:.2f}%",
        "bps": f"{v:.0f} bps",
        "usd": f"${v:,.2f}",
        "ratio": f"{v:.4f}",
    }.get(unit, f"{v:,.2f}")


def _summarize_one(s: pd.Series, unit: str) -> dict:
    """s: values indexed by date, sorted ascending."""
    last, last_date = s.iloc[-1], s.index[-1]

    # Yields and spreads change in bps; everything else in %.
    if unit in ("pct", "bps"):
        mult = 100 if unit == "pct" else 1
        chg_unit = "bps"
        def change_from(base): return (last - base) * mult
        daily = s.diff() * mult
    else:
        chg_unit = "%"
        def change_from(base): return (last / base - 1) * 100
        daily = (s / s.shift(1) - 1) * 100

    week_base = s.asof(last_date - pd.Timedelta(days=7))
    prior_year = s[s.index.year < last_date.year]
    ytd_base = prior_year.iloc[-1] if len(prior_year) else np.nan

    sd = daily.iloc[-(Z_WINDOW + 1):-1].std()
    d1 = daily.iloc[-1]

    return {
        "date": last_date,
        "level": last,
        "level_str": _fmt_level(last, unit),
        "chg_unit": chg_unit,
        "1D": d1,
        "1W": change_from(week_base),
        "YTD": change_from(ytd_base),
        "z": d1 / sd if sd and not np.isnan(sd) else np.nan,
        "pctl": (s <= last).mean() * 100,  # percentile vs full stored history
        "spark": s.iloc[-SPARK_WINDOW:].tolist(),
    }


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """One row per series with level, changes, percentile, z-score, sparkline."""
    rows = []
    for (section, metric, sid, unit), g in df.groupby(
        ["section", "metric", "series_id", "unit"], observed=True, sort=False
    ):
        s = g.sort_values("date").set_index("date")["value"]
        if len(s) < 2:
            continue
        rows.append({"section": section, "metric": metric, "series_id": sid,
                     **_summarize_one(s, unit)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- rendering

def _state_strip(summ: pd.DataFrame) -> None:
    by_id = summ.set_index("series_id")
    cols = st.columns(len(STATE_STRIP))
    for col, (sid, label, delta_color) in zip(cols, STATE_STRIP):
        if sid not in by_id.index:
            continue
        r = by_id.loc[sid]
        delta = f"{r['1D']:+.1f} bps" if r["chg_unit"] == "bps" else f"{r['1D']:+.2f}%"
        col.metric(label, r["level_str"], delta=delta, delta_color=delta_color)


def _what_moved(summ: pd.DataFrame, n: int = 3) -> None:
    movers = summ.dropna(subset=["z"]).assign(abs_z=lambda d: d["z"].abs())
    movers = movers.nlargest(n, "abs_z")
    if movers.empty:
        return
    parts = []
    for _, r in movers.iterrows():
        chg = f"{r['1D']:+.1f} bps" if r["chg_unit"] == "bps" else f"{r['1D']:+.2f}%"
        parts.append(f"**{r['metric']}** {chg} ({r['z']:+.1f}σ)")
    st.markdown("**What moved:** " + " · ".join(parts))


def _panel(summ: pd.DataFrame, section: str, title: str, as_of: pd.Timestamp) -> None:
    t = summ[summ["section"] == section].copy()
    if t.empty:
        return
    st.subheader(title)

    # Flag series whose latest observation is older than the dashboard date.
    stale = t["date"] < as_of
    t.loc[stale, "metric"] = t.loc[stale].apply(
        lambda r: f"{r['metric']} ({r['date']:%m/%d})", axis=1
    )

    fmt = "%+.1f bps" if t["chg_unit"].iloc[0] == "bps" else "%+.2f%%"
    st.dataframe(
        t[["metric", "level_str", "1D", "1W", "YTD", "pctl", "spark"]],
        hide_index=True,
        width="stretch",  # older Streamlit: use_container_width=True
        column_config={
            "metric": st.column_config.TextColumn(""),
            "level_str": st.column_config.TextColumn("Level"),
            "1D": st.column_config.NumberColumn("1D", format=fmt),
            "1W": st.column_config.NumberColumn("1W", format=fmt),
            "YTD": st.column_config.NumberColumn("YTD", format=fmt),
            "pctl": st.column_config.ProgressColumn(
                "3Y pctl", min_value=0, max_value=100, format="%.0f"
            ),
            "spark": st.column_config.LineChartColumn(f"Last {SPARK_WINDOW}d"),
        },
    )


def render(df: pd.DataFrame, data_warnings: list[str] | None = None) -> None:
    summ = summarize(df)
    as_of = df["date"].max()

    st.title("Market Dashboard")
    st.caption(f"As of {as_of:%a %b %d, %Y} close")

    _state_strip(summ)
    _what_moved(summ)
    st.divider()

    for i in range(0, len(PANELS), 2):
        left, right = st.columns(2)
        for col, (section, title) in zip((left, right), PANELS[i:i + 2]):
            with col:
                _panel(summ, section, title, as_of)

    if data_warnings:
        with st.expander(f"Data checks ({len(data_warnings)})"):
            for w in data_warnings:
                st.warning(w)