import warnings

import streamlit as st

from format_metrics import render
from get_metrics import get_metrics

st.set_page_config(page_title="Market Dashboard", page_icon="📈", layout="wide")


@st.cache_data(ttl=3600, show_spinner="Pulling market data…")
def load():
    # Capture validate()'s warnings so they show in the UI, not just the terminal.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        df = get_metrics()
    return df, [str(w.message) for w in caught]


df, data_warnings = load()
render(df, data_warnings)