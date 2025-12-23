import streamlit as st
from streamlit_autorefresh import st_autorefresh
from scraper import fetcher
import pandas as pd

st.set_page_config(page_title="XRP Trade Dashboard", layout="centered")
st.title("XRP Live Price Tracker")

# refresh every 1 second
st_autorefresh(interval=1000, key="price_refresh")

# -----------------------------------
# Live price (SAFE)
# -----------------------------------
current_price = 0.0  # ✅ always defined

try:
    current_price = fetcher("XRPUSDT")
    st.metric("XRP/USDT", f"${current_price:,.4f}")
except Exception as e:
    st.error(f"Failed to fetch price: {e}")

# -----------------------------------
# CSV persistence
# -----------------------------------
csv_file = "my_xrp_trades.csv"

if "trades" not in st.session_state:
    try:
        st.session_state.trades = pd.read_csv(csv_file)

        st.session_state.trades["Amount USDT"] = pd.to_numeric(
            st.session_state.trades["Amount USDT"], errors="coerce"
        )
        st.session_state.trades["Buy Price"] = pd.to_numeric(
            st.session_state.trades["Buy Price"], errors="coerce"
        )

        if "Date (optional)" in st.session_state.trades.columns:
            st.session_state.trades["Date (optional)"] = (
                pd.to_datetime(
                    st.session_state.trades["Date (optional)"], errors="coerce"
                ).dt.date
            )

    except FileNotFoundError:
        st.session_state.trades = pd.DataFrame(
            {
                "Amount USDT": [10.90],
                "Buy Price": [1.8660],
                "Date (optional)": [pd.Timestamp("2025-12-20").date()],
            }
        )

# -----------------------------------
# Sidebar editor
# -----------------------------------
st.sidebar.header("📝 Your XRP Buys (Add all purchases)")

trades = st.sidebar.data_editor(
    st.session_state.trades,
    num_rows="dynamic",
    column_config={
        "Amount USDT": st.column_config.NumberColumn(
            "Amount USDT", min_value=0.01, step=0.01, format="%.2f"
        ),
        "Buy Price": st.column_config.NumberColumn(
            "Buy Price ($)", min_value=0.01, step=0.0001, format="%.4f"
        ),
        "Date (optional)": st.column_config.DateColumn("Date (optional)"),
    },
    width="stretch",  # ✅ replaces deprecated use_container_width
    hide_index=True,
)

st.session_state.trades = trades
trades.to_csv(csv_file, index=False)

# -----------------------------------
# Calculations
# -----------------------------------
total_invested = trades["Amount USDT"].sum()
total_xrp_from_trades = (trades["Amount USDT"] / trades["Buy Price"]).sum()
average_buy_price = (
    total_invested / total_xrp_from_trades if total_xrp_from_trades > 0 else 0
)

# Manual override
st.sidebar.divider()
manual_balance = st.sidebar.text_input(
    "🔧 Manual XRP Balance Override (optional)", placeholder="e.g., 5.846321"
)

if manual_balance.strip():
    try:
        amount_held = float(manual_balance)
        st.sidebar.info("Using manual XRP balance override")
    except ValueError:
        st.sidebar.error("Invalid manual balance")
        amount_held = total_xrp_from_trades
else:
    amount_held = total_xrp_from_trades

# Final values
if current_price > 0 and amount_held > 0:
    current_value = amount_held * current_price
    profit = current_value - total_invested
    percentage = (profit / total_invested) * 100 if total_invested > 0 else 0
else:
    current_value = profit = percentage = 0


st.header("📊 Position Summary")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total XRP Held", f"{amount_held:.6f}")
c2.metric("Total Invested", f"${total_invested:.2f}")
c3.metric("Average Buy Price", f"${average_buy_price:.4f}")
c4.metric("Current Value", f"${current_value:.2f}")

st.divider()

if profit >= 0:
    st.success(f"✅ Unrealized Profit: **${profit:.2f}** (+{percentage:.2f}%)")
else:
    st.error(f"❌ Unrealized Loss: **${profit:.2f}** ({percentage:.2f}%)")

with st.expander("View Trade Details"):
    st.dataframe(
        trades.style.format(
            {"Amount USDT": "${:.2f}", "Buy Price": "${:.4f}"}
        )
    )

    st.write(
        f"""
        - **Live Price**: ${current_price:.4f}
        - **Current Value**: ${current_value:.4f}
        - **Total Invested**: ${total_invested:.2f}
        """
    )

st.caption("Data saved to 'my_xrp_trades.csv'. Add new buys anytime 🚀")
