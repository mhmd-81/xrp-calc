# from binance.client import Client

# PROXY_URL = 'socks5h://127.0.0.1:10808' 

# proxies = {
#     'http': PROXY_URL,
#     'https': PROXY_URL,
# }

# client = Client(
#     requests_params={
#         'proxies': proxies,
#         'timeout': 30  
#     }
# )


# client = Client()

# def fetcher(coin):
#         data = client.get_symbol_ticker(symbol = coin)
#         return float(data['price']) 


from binance.client import Client

# PROXY_URL = 'socks5h://127.0.0.1:10808'
# proxies = {
#     'http': PROXY_URL,
#     'https': PROXY_URL,
# }


# client = Client(
#     requests_params={
#         'proxies': proxies,
#         'timeout': 30
#     }
# )


def fetcher(coin):
    data = Client.get_symbol_ticker(symbol=coin)
    return float(data['price'])

# Test it
if __name__ == "__main__":
    try:
        price = fetcher("XRPUSDT")
        print("XRP price:", price)
    except Exception as e:
        print("Error:", e)
