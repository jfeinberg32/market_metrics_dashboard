import datetime as dt
import streamlit as st
from get_metrics import get_metrics 
from format_metrics import render

@st.cache_data
def load(day: dt.date):
    return get_metrics()

raw = load(dt.date.today())
render(raw, as_of="Oct 5, 2026")

#data = load(dt.date.today())
#st.title(f"Market Metrics — {dt.date.today()}")

#st.subheader("Weekly Metrics")
#st.table(data)