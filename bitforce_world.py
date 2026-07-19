import streamlit as st
import os
import pandas as pd

# Page Config with Dark/Professional styling hints
st.set_page_config(page_title="Bitforce Dashboard", layout="wide")

# Custom CSS for premium card container design
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .custom-header {
        color: #1E3A8A;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialize
if "investment" not in st.session_state:
    st.session_state.investment = 100.0
if "initial_investment" not in st.session_state:
    st.session_state.initial_investment = 100.0
if "main_wallet" not in st.session_state:
    st.session_state.main_wallet = 0.0
if "support_wallet" not in st.session_state:
    st.session_state.support_wallet = 0.0
if "history" not in st.session_state:
    st.session_state.history = []
if "current_cycle_idx" not in st.session_state:
    st.session_state.current_cycle_idx = 0

cycle_names = ["1st Cycle", "2nd Cycle", "3rd Cycle", "4th Cycle", "5th Cycle", "6th Cycle", "7th Cycle"]
cycle_options = [10, 15, 20, 25, 30, 35, 40]
interest_map = {10: 15, 15: 30, 20: 50, 25: 75, 30: 100, 35: 150, 40: 200}

# ==================== SIDEBAR LAYOUT (Left Side) ====================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("💼 Bitforce")
    
    st.write("---")
    st.header("⚙️ Operations Panel")
    
    # Current active state indicators
    current_cycle_name = cycle_names[min(st.session_state.current_cycle_idx, 6)]
    st.subheader(f"📍 Active: {current_cycle_name}")
    
    inv_value = st.number_input(
        "Active Investment ($)",
        min_value=0.0,
        value=float(st.session_state.investment),
        step=10.0,
    )
    
    # Lock the first initial investment amount for theoretical calculation map
    if st.session_state.current_cycle_idx == 0:
        st.session_state.initial_investment = inv_value
    
    selected_cycle = st.selectbox("Select Cycle Duration (Days)", options=cycle_options, index=min(st.session_state.current_cycle_idx, 6))
    
    # Process Button
    if st.button("🚀 Process & Close Active Cycle"):
        if inv_value < 20.0:
            st.error("Minimum Investment is $20.")
        elif st.session_state.current_cycle_idx >= 7:
            st.warning("All 7 cycles completed! Please reset to start fresh.")
        else:
            interest_rate = interest_map[selected_cycle]
            profit = (inv_value * interest_rate) / 100
            
            main_share = inv_value + (profit * 0.70)
            support_share = profit * 0.30
            
            st.session_state.main_wallet += main_share
            st.session_state.support_wallet += support_share
            
            # Log initial step without withdrawal
            st.session_state.history.append({
                "Cycle": current_cycle_name,
                "Invested": inv_value,
                "Days": f"{selected_cycle} Days",
                "Interest": f"{interest_rate}%",
                "Profit Generated": profit,
                "Withdrawal (Main)": 0.0,
                "Support Auto Re-Invest": 0.0,
                "Status": "Profit Distributed"
            })
            st.session_state.current_cycle_idx += 1
            st.rerun()

    st.write("---")
    st.header("💸 Actions: Pay Out / Reinvest")
    
    # Main Wallet Withdrawal (Allows full precision input)
    max_m_w = st.session_state.main_wallet
    main_withdraw_amt = st.number_input("Withdraw from Main Wallet ($)", min_value=0.0, max_value=float(max_m_w), value=0.0, step=0.01)
    
    # Support Wallet Info Display
    support_avail = st.session_state.support_wallet
    if support_avail >= 10.0:
        st.success(f"Support Base holds ${support_avail:.2f}. Perfect! It will be Auto Round Re-invested.")
    else:
        st.caption(f"🔒 Support Re-investment locked (Currently ${support_avail:.2f}, needs $10)")
        
    if st.button("🔄 Execute Settlements"):
        # 1. Main Wallet Calculation
        main_left = st.session_state.main_wallet - main_withdraw_amt
        main_round_reinvest = int(main_left)       # Round number for investment
        main_decimal_backup = main_left - main_round_reinvest # Decimals remain safe
        
        # 2. Support Wallet Calculation (Only triggers if balance >= 10)
        support_round_reinvest = 0
        support_left = support_avail
        
        if support_avail >= 10.0:
            support_round_reinvest = int(support_avail)
            support_left = support_avail - support_round_reinvest # Decimals remain safe
            
        # 3. Compile Total Round Capital for New Re-Investment
        st.session_state.investment = float(main_round_reinvest + support_round_reinvest)
        
        # Save updated decimal fragments back to system wallets
        st.session_state.main_wallet = main_decimal_backup
        st.session_state.support_wallet = support_left
        
        # Calculate compound loss warning message if withdrawal happened
        if main_withdraw_amt > 0:
            projected_loss = main_withdraw_amt * 2.5 
            st.session_state.last_warning = f"⚠️ Alert: Apne Main Wallet se ${main_withdraw_amt:.2f} withdraw kiya. Agar ye amount system me compound hota to 7th cycle tak aap lagbhag ${projected_loss:.2f} extra earn kar sakte the!"
        
        # Update last history logs
        if st.session_state.history:
            st.session_state.history[-1]["Withdrawal (Main)"] = main_withdraw_amt
            st.session_state.history[-1]["Support Auto Re-Invest"] = float(support_round_reinvest)
            st.session_state.history[-1]["Status"] = "Settled & Compound Re-routed"
            
        st.rerun()

    if st.button("🧹 Reset Whole Lifecycle"):
        st.session_state.clear()
        st.rerun()


# ==================== MAIN DASHBOARD DISPLAY (Right Side) ====================
st.markdown("<h2 class='custom-header'>📈 Bitforce Live Ledger Engine</h2>", unsafe_allow_html=True)

# Top Bar Metrics Grid
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("💼 Active Capital Base", f"${st.session_state.investment:.2f}")
with col_m2:
    st.metric("💰 Main Wallet Core Balance", f"${st.session_state.main_wallet:.2f}")
with col_m3:
    st.metric("🛡️ Support Wallet Rolling Base", f"${st.session_state.support_wallet:.2f}")

if "last_warning" in st.session_state and st.session_state.last_warning:
    st.warning(st.session_state.last_warning)
    st.session_state.last_warning = "" # Clear after one flash

st.write("---")

# Dynamic Current Flow Sheet Table
st.subheader("📋 Active Lifecycle Statement (Live Steps Track)")
if st.session_state.history:
    df_history = pd.DataFrame(st.session_state.history)
    st.dataframe(df_history.set_index("Cycle"), use_container_width=True)
else:
    st.info("Pehle Left Sidebar se 'Complete Cycle & Process Profit' par click karein. Jaise-jaise aap aage badhenge, aapka real-time custom workflow yahan load hoga.")

st.write("---")

# Projection Analysis Block - FIXED & ENFORCING THE $10 BLOCK CONDITION
st.subheader("🔮 Theoretical Compounding Map (If 0% Withdrawal Maintained From Start)")
st.caption(f"Fixed Map Base Calculation Level Set On Initial Entry: **${st.session_state.initial_investment:.2f}** (Support balance only compounds when it accumulates to $10+)")

days_list = [10, 15, 20, 25, 30, 35, 40]
pct_list = [15, 30, 50, 75, 100, 150, 200]

proj_data = []
temp_cap = st.session_state.initial_investment
virtual_support_wallet = 0.0

for i in range(7):
    p_prof = (temp_cap * pct_list[i]) / 100
    m_70 = p_prof * 0.70
    s_30 = p_prof * 0.30
    
    # Virtual support wallet gets its 30% allocation
    virtual_support_wallet += s_30
    
    # 70% goes straight to Main, and the initial active capital returns
    next_reinvest_pool = temp_cap + m_70
    
    # Check if support wallet hit the strict $10 threshold limit
    support_release = 0
    if virtual_support_wallet >= 10.0:
        support_release = int(virtual_support_wallet)
        virtual_support_wallet = virtual_support_wallet - support_release
        
    # The absolute next target base
    nxt = next_reinvest_pool + support_release
    
    proj_data.append({
        "Cycle Stage": cycle_names[i],
        "Duration": f"{days_list[i]} Days",
        "ROI": f"{pct_list[i]}%",
        "Expected Profit": f"${p_prof:.2f}",
        "Main Allocation": f"${m_70:.2f}",
        "Support Allocation (Current Cycle)": f"${s_30:.2f}",
        "Support Vault Roll over Balance": f"${virtual_support_wallet:.2f}",
        "Perfect Reinvest Target": f"${int(nxt)}"
    })
    temp_cap = float(int(nxt)) # Re-invest operates on rounded amounts

df_proj = pd.DataFrame(proj_data)
st.table(df_proj.set_index("Cycle Stage"))
