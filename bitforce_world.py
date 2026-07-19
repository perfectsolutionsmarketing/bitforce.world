import streamlit as st
import os
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Bitforce Investment Portal", layout="centered")

# 0. Logo Section - Size fixed to 300px and centered
if os.path.exists("logo.png"):
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.image("logo.png", width=300)
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

default_inv = float(st.session_state.investment) if st.session_state.investment > 0 else 100.0

inv_value = st.number_input(
    "Investment Value ($)",
    min_value=0.0,
    value=default_inv,
    step=10.0,
)

cycle_options = [10, 15, 20, 25, 30, 35, 40]
interest_map = {10: 15, 15: 30, 20: 50, 25: 75, 30: 100, 35: 150, 40: 200}
cycle_names = ["1st Cycle", "2nd Cycle", "3rd Cycle", "4th Cycle", "5th Cycle", "6th Cycle", "7th Cycle"]

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
    st.rerun()

st.write("---")

# 5. Dynamic Bitforce Investment Projection Sheets
st.header("📋 Bitforce Investment Plan Projections")
st.caption(f"Based on current input value: **${inv_value:.2f}**")

# --- DATA GENERATION FOR TABLES ---
days_list = [10, 15, 20, 25, 30, 35, 40]
pct_list = [15, 30, 50, 75, 100, 150, 200]

# Scenario A: 100% Compounding (0% Withdrawal)
data_a = []
current_principal_a = inv_value
for i in range(7):
    day = days_list[i]
    pct = pct_list[i]
    profit = (current_principal_a * pct) / 100
    main_70 = profit * 0.70
    e_wallet_30 = profit * 0.30
    
    # Next Re-invest is Principal + Total Profit (since 0% withdrawal)
    next_reinvest = current_principal_a + profit
    
    data_a.append({
        "Cycle": cycle_names[i],
        "Days": f"{day} Days",
        "Interest": f"{pct}%",
        "Profits": f"${profit:.2f}",
        "Main Wallet (70%)": f"${main_70:.2f}",
        "E-Wallet (30%)": f"${e_wallet_30:.2f}",
        "Re-Invest": f"${int(next_reinvest)}"
    })
    current_principal_a = next_reinvest

df_a = pd.DataFrame(data_a)

# Scenario B: 30% Support Wallet Compounding Only (70% Main Wallet Withdrawn)
data_b = []
current_principal_b = inv_value
total_net_withdrawal = 0.0

for i in range(7):
    day = days_list[i]
    pct = pct_list[i]
    profit = (current_principal_b * pct) / 100
    main_70 = profit * 0.70
    e_wallet_30 = profit * 0.30
    
    # 70% of profit + principal is taken out, only 30% support wallet is reinvested
    next_reinvest = current_principal_b + e_wallet_30
    total_net_withdrawal += main_70
    
    data_b.append({
        "Cycle": cycle_names[i],
        "Days": f"{day} Days",
        "Interest": f"{pct}%",
        "Profits": f"${profit:.2f}",
        "Main Wallet (70%)": f"${main_70:.2f}",
        "E-Wallet (30%)": f"${e_wallet_30:.2f}",
        "Re-Invest": f"${int(next_reinvest)}"
    })
    current_principal_b = next_reinvest

df_b = pd.DataFrame(data_b)

# --- DISPLAY SHEET 1 ---
st.subheader("🔴 Incase When 0% Withdrawal and Compounding All Profit & Principal")
st.table(df_a.set_index("Cycle"))
st.metric(label="Net Compounded Value at 7th Cycle", value=f"${int(current_principal_a)}")

st.write("---")

# --- DISPLAY SHEET 2 ---
st.subheader("🔵 Incase when you invested only 30% of Support (E) Wallet")
st.table(df_b.set_index("Cycle"))

col_b1, col_b2 = st.columns(2)
with col_b1:
    st.metric(label="Total Net Withdrawal (70% Part)", value=f"${total_net_withdrawal:.2f}")
with col_b2:
    st.metric(label="Final Invested Value at 7th Cycle", value=f"${int(current_principal_b)}")
