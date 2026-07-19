import streamlit as st
import os

# Page Configuration
st.set_page_config(page_title="Bitforce Investment Portal", layout="centered")

# 0. Logo & Company Title Header (Updated for logo.png)
if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)
else:
    st.title("💼 Bitforce Investment Portal")

st.write("---")

# Session State Initialize
if "investment" not in st.session_state:
    st.session_state.investment = 0.0
if "main_wallet" not in st.session_state:
    st.session_state.main_wallet = 0.0
if "support_wallet" not in st.session_state:
    st.session_state.support_wallet = 0.0

# 1. Input Section
st.header("1. New / Active Investment")

default_inv = float(st.session_state.investment) if st.session_state.investment > 0 else 20.0

inv_value = st.number_input(
    "Investment Value ($)",
    min_value=0.0,
    value=default_inv,
    step=10.0,
)

cycle_options = [10, 15, 20, 25, 30, 35, 40]
interest_map = {10: 15, 15: 30, 20: 50, 25: 75, 30: 100, 35: 150, 40: 200}

selected_cycle = st.selectbox("Select Cycle (Days)", options=cycle_options)

# 2. Calculate Cycle Completion
if st.button("Complete Cycle & Process Profit"):
    if inv_value < 20.0:
        st.error("❌ Error: Minimum Investment Value must be $20 or more.")
    else:
        st.session_state.investment = inv_value
        interest_rate = interest_map[selected_cycle]

        total_profit = (st.session_state.investment * interest_rate) / 100

        main_wallet_share = st.session_state.investment + (total_profit * 0.70)
        new_support_share = total_profit * 0.30
        
        st.session_state.support_wallet += new_support_share
        st.session_state.main_wallet += main_wallet_share

        st.success(f"🎉 {selected_cycle} Days Cycle Completed! Profit generated: {interest_rate}%")

st.write("---")

# 3. Wallet Dashboard Display
st.header("📊 Wallet Balances")
col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="Main Wallet Balance",
        value=f"${st.session_state.main_wallet:.2f}",
    )

with col2:
    st.metric(
        label="Support Wallet Balance",
        value=f"${st.session_state.support_wallet:.2f}",
    )

st.write("---")

# 4. Withdrawal & Re-investment Section
st.header("💸 Withdrawal & Re-investment")

max_main_withdraw = st.session_state.main_wallet
main_withdraw_amt = st.number_input(
    "Amount to Withdraw from Main Wallet ($)",
    min_value=0.0,
    max_value=float(max_main_withdraw),
    value=0.0,
    step=1.0,
)

support_available = st.session_state.support_wallet
can_withdraw_support = support_available >= 10.0
support_withdraw_amt = 0.0

if can_withdraw_support:
    max_support_withdraw = int(support_available)
    st.info(f"Support wallet has ${support_available:.2f}. You can withdraw up to ${max_support_withdraw} (Round Amount Only).")
    support_withdraw_amt = st.number_input(
        "Amount to Withdraw from Support Wallet ($)",
        min_value=0,
        max_value=max_support_withdraw,
        value=0,
        step=1,
    )
else:
    st.warning("Support Wallet balance is less than $10. Withdrawal locked for this wallet.")


if st.button("Process Withdrawal & Re-invest Balance"):
    main_balance_left = st.session_state.main_wallet - main_withdraw_amt
    main_round_invest = int(main_balance_left) 
    main_decimal_left = main_balance_left - main_round_invest 

    support_balance_left = st.session_state.support_wallet - float(support_withdraw_amt)
    
    support_reinvest_amt = 0
    if support_balance_left >= 10.0:
        support_reinvest_amt = int(support_balance_left)
        support_balance_left = support_balance_left - support_reinvest_amt 

    st.session_state.investment = float(main_round_invest + support_reinvest_amt)
    st.session_state.main_wallet = main_decimal_left
    st.session_state.support_wallet = support_balance_left

    st.success("Withdrawal & Re-investment Processed Successfully!")
    
    st.info(f"New Active Investment Value: ${st.session_state.investment:.2f}")
    if support_reinvest_amt > 0:
        st.caption(f"Note: Included ${support_reinvest_amt} automatically from Support Wallet (Balance was >= $10)")
        
    st.info(f"Main Wallet Rolling Balance (Decimals): ${st.session_state.main_wallet:.2f}")
    st.info(f"Support Wallet Rolling Balance (Decimals): ${st.session_state.support_wallet:.2f}")

    st.rerun()
