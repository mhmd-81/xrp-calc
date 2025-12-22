import streamlit as st
from streamlit_autorefresh import st_autorefresh
from scraper import fetcher
import pandas as pd

st.set_page_config(page_title="XRP Trade Dashboard", layout="centered")
st.title("XRP Live Price Tracker")

# refresh every 1 second
st_autorefresh(interval=1000, key="price_refresh")

try:
    current_price = fetcher("XRPUSDT")
    st.metric("XRP/USDT", f"${float(current_price):,.4f}")
except Exception as e:
    st.error(f"Failed to fetch price: {e}")

balance = st.text_input("Enter your balance")

# st.sidebar.header("Your Trade Details")
# asset = st.sidebar.text_input("Asset", value="XRP")
# investment = st.sidebar.number_input("Investment Amount (USDT/$)", value=10.90, min_value=0.0, step=0.01)
# buy_price = st.sidebar.number_input("Your Buy Price (per XRP)", value=1.8660, min_value=0.0, step=0.0001)
# balance_input = st.sidebar.text_input("Optional: Manual XRP Balance Override", value="")


# if current_price > 0 and buy_price > 0:
#     if balance_input and float(balance_input or 0) > 0:
#         amount_bought = float(balance_input)
#         st.sidebar.info("Using manual balance")
#     else:
#         amount_bought = investment / buy_price

#     current_value = amount_bought * current_price
#     profit = current_value - investment
#     percentage_gain = (profit / investment) * 100 if investment > 0 else 0.0

#     st.header("📊 Position Summary")
#     col1, col2, col3 = st.columns(3)
#     col1.metric("Amount Held", f"{amount_bought:.4f} {asset}")
#     col2.metric("Current Value", f"${current_value:.2f}")
#     col3.metric("Profit/Loss", f"${profit:+.2f}", delta=f"{percentage_gain:+.2f}%")

#     if profit >= 0:
#         st.success(f"✅ Profit: **${profit:.2f}** (+{percentage_gain:.2f}%)")
#     else:
#         st.error(f"❌ Loss: **${profit:.2f}** ({percentage_gain:.2f}%)")

#     st.write(f"""
#     - Bought **{amount_bought:.4f} {asset}** at **${buy_price:.4f}**  
#     - Invested: **${investment:.2f}**  
#     - Live price: **${current_price:.4f}** → Worth **${current_value:.2f}**
#     """)


csv_file = "my_xrp_trades.csv"
if 'trades' not in st.session_state:
    try:
        st.session_state.trades = pd.read_csv(csv_file)
        # Ensure correct column types
        st.session_state.trades["Amount USDT"] = pd.to_numeric(st.session_state.trades["Amount USDT"], errors='coerce')
        st.session_state.trades["Buy Price"] = pd.to_numeric(st.session_state.trades["Buy Price"], errors='coerce')
        if "Date (optional)" in st.session_state.trades.columns:
            st.session_state.trades["Date (optional)"] = pd.to_datetime(st.session_state.trades["Date (optional)"], errors='coerce').dt.date
    except FileNotFoundError:
        # Default: your original buy
        st.session_state.trades = pd.DataFrame({
            "Amount USDT": [10.90],
            "Buy Price": [1.8660],
            "Date (optional)": [pd.Timestamp('2025-12-20').date()]
        })

# Sidebar: Editable trade history
st.sidebar.header("📝 Your XRP Buys (Add all purchases)")

trades = st.sidebar.data_editor(
    st.session_state.trades,
    num_rows="dynamic",
    column_config={
        "Amount USDT": st.column_config.NumberColumn("Amount USDT", min_value=0.01, step=0.01, format="%.2f"),
        "Buy Price": st.column_config.NumberColumn("Buy Price ($)", min_value=0.01, step=0.0001, format="%.4f"),
        "Date (optional)": st.column_config.DateColumn("Date (optional)"),
    },
    use_container_width=True,
    hide_index=True
)

# Save updated trades back to session and CSV
st.session_state.trades = trades
trades.to_csv(csv_file, index=False)

# Calculate totals from trades
total_invested = trades["Amount USDT"].sum()
total_xrp_from_trades = (trades["Amount USDT"] / trades["Buy Price"]).sum()
average_buy_price = total_invested / total_xrp_from_trades if total_xrp_from_trades > 0 else 0

# Manual override option
st.sidebar.divider()
manual_balance = st.sidebar.text_input("🔧 Manual XRP Balance Override (optional)", value="", placeholder="e.g., 5.846321")

if manual_balance and manual_balance.strip():
    try:
        amount_held = float(manual_balance)
        st.sidebar.info("Using manual XRP balance override")
    except:
        st.sidebar.error("Invalid manual balance")
        amount_held = total_xrp_from_trades
else:
    amount_held = total_xrp_from_trades

# Final calculations
if current_price > 0 and amount_held > 0:
    current_value = amount_held * current_price
    profit = current_value - total_invested
    percentage = (profit / total_invested) * 100 if total_invested > 0 else 0
else:
    current_value = profit = percentage = 0

# Main display
st.header("📊 Position Summary")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total XRP Held", f"{amount_held:.6f}")
col2.metric("Total Invested", f"${total_invested:.2f}")
col3.metric("Average Buy Price", f"${average_buy_price:.4f}")
col4.metric("Current Value", f"${current_value:.2f}")

st.divider()

# Profit/Loss highlight
if profit >= 0:
    st.success(f"✅ Unrealized Profit: **${profit:.2f}** (+{percentage:.2f}%)")
else:
    st.error(f"❌ Unrealized Loss: **${profit:.2f}** ({percentage:.2f}%)")

# Details
with st.expander("View Trade Details"):
    st.dataframe(trades.style.format({
        "Amount USDT": "${:.2f}",
        "Buy Price": "${:.4f}"
    }))

    st.write(f"""
    - **Live Price**: ${current_price:.4f}
    - **Current Value**: ${current_value:.4f}
    - **Total Invested**: ${total_invested:.2f}
    """)

st.caption("Data saved to 'my_xrp_trades.csv'. Add new buys anytime! Next: charts & stop-loss alerts 🚀")