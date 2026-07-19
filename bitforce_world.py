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
                "Withdrawal (Support)": 0.0,
                "Status": "Profit Distributed"
            })
            st.session_state.current_cycle_idx += 1
            st.rerun()

    st.write("---")
    st.header("💸 Actions: Pay Out / Reinvest")
    
    # Main Wallet Withdrawal
    max_m_w = st.session_state.main_wallet
    main_withdraw_amt = st.number_input("Withdraw from Main Wallet ($)", min_value=0.0, max_value=float(max_m_w), value=0.0)
    
    # Support Wallet Withdrawal
    support_avail = st.session_state.support_wallet
    support_withdraw_amt = 0.0
    if support_avail >= 10.0:
        max_s_w = int(support_avail)
        support_withdraw_amt = st.number_input("Withdraw from Support ($ Round)", min_value=0, max_value=max_s_w, value=0)
    else:
        st.caption("🔒 Support wallet locked (< $10)")
        
    if st.button("🔄 Execute Settlements"):
        # Calculate Remaining
        main_left = st.session_state.main_wallet - main_withdraw_amt
        m_round = int(main_left)
        m_dec = main_left - m_round
        
        sup_left = st.session_state.support_wallet - float(support_withdraw_amt)
        s_reinvest = 0
        if sup_left >= 10.0:
            s_reinvest = int(sup_left)
            sup_left = sup_left - s_reinvest
            
        # Update session states
        st.session_state.investment = float(m_round + s_reinvest)
        st.session_state.main_wallet = m_dec
        st.session_state.support_wallet = sup_left
        
        # Calculate compound loss warning message if withdrawal happened
        total_withdrawn = main_withdraw_amt + support_withdraw_amt
        if total_withdrawn > 0:
            # Simple 7-cycle potential projection calculation for alert
            projected_loss = total_withdrawn * 2.5 
            st.session_state.last_warning = f"⚠️ Alert: Apne ${total_withdrawn:.2f} withdraw kiya. Agar ye asset system me rehta toh compounding ke sath 7th cycle tak aap ka lagbhag ${projected_loss:.2f} extra profit ban sakta tha!"
        
        # Update last history log status to show settlement changes
        if st.session_state.history:
            st.session_state.history[-1]["Withdrawal (Main)"] = main_withdraw_amt
            st.session_state.history[-1]["Withdrawal (Support)"] = support_withdraw_amt
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

# Projection Analysis Block
st.subheader("🔮 Theoretical Compounding Map (If 0% Withdrawal Maintained From Start)")
days_list = [10, 15, 20, 25, 30, 35, 40]
pct_list = [15, 30, 50, 75, 100, 150, 200]

base_calc = inv_value if inv_value >= 20 else 100.0
proj_data = []
temp_cap = base_calc

for i in range(7):
    p_prof = (temp_cap * pct_list[i]) / 100
    m_70 = p_prof * 0.70
    s_30 = p_prof * 0.30
    nxt = temp_cap + p_prof
    proj_data.append({
        "Cycle Stage": cycle_names[i],
        "Duration": f"{days_list[i]} Days",
        "ROI": f"{pct_list[i]}%",
        "Expected Profit": f"${p_prof:.2f}",
        "Main Allocation": f"${m_70:.2f}",
        "Support Allocation": f"${s_30:.2f}",
        "Perfect Reinvest Target": f"${int(nxt)}"
    })
    temp_cap = nxt

df_proj = pd.DataFrame(proj_data)
st.table(df_proj.set_index("Cycle Stage"))
