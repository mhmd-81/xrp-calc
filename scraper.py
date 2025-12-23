import streamlit as st
import requests
from binance.client import Client

_client = Client()

@st.cache_data(ttl=2)
def fetcher(symbol):
    try:
        data = _client.get_symbol_ticker(symbol=symbol)
        return float(data["price"])
    except Exception:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "ripple", "vs_currencies": "usd"},
            timeout=10,
        )
        r.raise_for_status()
        return float(r.json()["ripple"]["usd"])
