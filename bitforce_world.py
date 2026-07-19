import streamlit as st

# Page Configuration
st.set_page_config(page_title="Bitforce Investment Portal", layout="centered")

# Company Name Title
st.title("💼 Bitforce Investment Portal")
st.write("---")

# Session State Initialize (Data ko save rakhne ke liye)
if "investment" not in st.session_state:
    st.session_state.investment = 0.0
if "main_wallet" not in st.session_state:
    st.session_state.main_wallet = 0.0
if "support_wallet" not in st.session_state:
    st.session_state.support_wallet = 0.0

# 1. Input Section
st.header("1. New / Active Investment")

# Agar pehle se koi reinvested amount hai toh wo default value ban jayegi
inv_value = st.number_input(
    "Investment Value ($)",
    min_value=0.0,
    value=float(st.session_state.investment)
    if st.session_state.investment > 0
    else 100.0,
    step=10.0,
)

# Cycle Days Options & Interest Mapping
cycle_options = [10, 15, 20, 25, 30, 35, 40]
interest_map = {10: 15, 15: 30, 20: 50, 25: 75, 30: 100, 35: 150, 40: 200}

selected_cycle = st.selectbox("Select Cycle (Days)", options=cycle_options)

# 2. Calculate Cycle Completion
if st.button("Complete Cycle & Process Profit"):
    st.session_state.investment = inv_value
    interest_rate = interest_map[selected_cycle]

    # Profit Calculation
    total_profit = (st.session_state.investment * interest_rate) / 100

    # Wallet Splitting Logic
    # Main Wallet = Principal + 70% of Profit
    main_wallet_share = st.session_state.investment + (total_profit * 0.70)

    # Support Wallet = 30% of Profit + Purana bacha hua Support Balance
    new_support_share = total_profit * 0.30
    st.session_state.support_wallet += new_support_share

    st.session_state.main_wallet += main_wallet_share

    st.success(
        f"🎉 {selected_cycle} Days Cycle Completed! Profit generated: {interest_rate}%"
    )

st.write("---")

# 3. Wallet Dashboard Display
st.header("📊 Wallet Balances")
col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="Main Wallet (Principal + 70% Profit)",
        value=f"${st.session_state.main_wallet:.2f}",
    )

with col2:
    st.metric(
        label="Support Wallet (30% Profit)",
        value=f"${st.session_state.support_wallet:.2f}",
    )

st.write("---")

# 4. Withdrawal & Re-investment Section
st.header("💸 Withdrawal & Re-investment")

# Main Wallet Withdrawal Input
max_main_withdraw = st.session_state.main_wallet
main_withdraw_amt = st.number_input(
    "Amount to Withdraw from Main Wallet ($)",
    min_value=0.0,
    max_value=float(max_main_withdraw),
    value=0.0,
    step=1.0,
)

# Support Wallet Withdrawal Calculation
# Support se sirf tabhi nikalega jab > 10 ho, aur sirf Round (Integer) amount niklega.
support_available = st.session_state.support_wallet
can_withdraw_support = support_available >= 10.0
support_withdraw_amt = 0.0

if can_withdraw_support:
    # Sirf integer/round part withdraw ke liye allow karenge
    max_support_withdraw = int(support_available)
    st.info(
        f"Support wallet has more than $10. You can withdraw up to ${max_support_withdraw} (Round Amount Only)."
    )
    support_withdraw_amt = st.number_input(
        "Amount to Withdraw from Support Wallet ($)",
        min_value=0,
        max_value=max_support_withdraw,
        value=0,
        step=1,
    )
else:
    st.warning(
        "Support Wallet balance is less than $10. Withdrawal locked for this wallet."
    )


if st.button("Process Withdrawal & Re-invest Balance"):
    # Main Wallet Process
    main_balance_left = st.session_state.main_wallet - main_withdraw_amt

    # Support Wallet Process
    # Decimal value automatic balance mein reh jayegi kyunki hum total se sirf selected round amount minus kar rahe hain
    support_balance_left = st.session_state.support_wallet - float(
        support_withdraw_amt
    )

    # Remaining balances ko hi next Investment value bana diya
    st.session_state.investment = main_balance_left
    st.session_state.support_wallet = support_balance_left

    # Reset Main wallet since its balance moved to Investment
    st.session_state.main_wallet = 0.0

    st.success("Withdrawal Processed Successfully!")
    st.info(
        f"New Active Investment Value for next cycle: ${st.session_state.investment:.2f}"
    )
    st.info(
        f"Support Wallet Rolling Balance (with Decimals): ${st.session_state.support_wallet:.2f}"
    )

    # Refresh page to update values
    st.rerun()
