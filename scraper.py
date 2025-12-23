import streamlit as st
from binance.client import Client

_client = Client()

@st.cache_data(ttl=2)
def fetcher(coin):
    data = _client.get_symbol_ticker(symbol=coin)
    return float(data["price"])

if __name__ == "__main__":
    try:
        price = fetcher("XRPUSDT")
        print("XRP price:", price)
    except Exception as e:
        print("Error:", e)
