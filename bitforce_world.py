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
if "workflow_status" not in st.session_state:
    st.session_state.workflow_status = ""
if "total_withdrawn" not in st.session_state:
    st.session_state.total_withdrawn = 0.0

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
            st.session_state.workflow_status = "awaiting_settlement"
            st.rerun()

    st.write("---")
    st.header("💸 Actions: Pay Out / Reinvest")
    
    # Smart Guard: Enable withdrawal only if cycle has processed profit but settlement hasn't closed it yet
    is_withdrawal_disabled = st.session_state.workflow_status != "awaiting_settlement"
    max_m_w = st.session_state.main_wallet
    
    if is_withdrawal_disabled and st.session_state.current_cycle_idx > 0:
        st.error("🔒 Re-investment locked! Naye cycle ka amount set ho chuka hai. Withdrawal ab agle cycle ke close hone par hi open hoga.")
        main_withdraw_amt = st.number_input("Withdraw from Main Wallet ($)", min_value=0.0, value=0.0, disabled=True)
    else:
        main_withdraw_amt = st.number_input("Withdraw from Main Wallet ($)", min_value=0.0, max_value=float(max_m_w), value=0.0, step=0.01)
    
    # Support Wallet Info Display
    support_avail = st.session_state.support_wallet
    if support_avail >= 10.0:
        st.success(f"Support Base holds ${support_avail:.2f}. Perfect! It will be Auto Round Re-invested.")
    else:
        st.caption(f"🔒 Support Re-investment locked (Currently ${support_avail:.2f}, needs $10)")
        
    # Execute Settlements Button control
    if st.button("🔄 Execute Settlements", disabled=is_withdrawal_disabled if st.session_state.current_cycle_idx > 0 else False):
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
        
        # Track historical global total withdrawals
        st.session_state.total_withdrawn += main_withdraw_amt
        
        # Save updated decimal fragments back to system wallets
        st.session_state.main_wallet = main_decimal_backup
        st.session_state.support_wallet = support_left
        
        # Update last history logs
        if st.session_state.history:
            st.session_state.history[-1]["Withdrawal (Main)"] = main_withdraw_amt
            st.session_state.history[-1]["Support Auto Re-Invest"] = float(support_round_reinvest)
            st.session_state.history[-1]["Status"] = "Settled & Compound Re-routed"
            
        st.session_state.workflow_status = "settled_done"
        st.rerun()

    if st.button("🧹 Reset Whole Lifecycle"):
        st.session_state.clear()
        st.rerun()


# ==================== MAIN DASHBOARD DISPLAY (Right Side) ====================
st.markdown("<h2 class='custom-header'>📈 Bitforce Live Ledger Engine</h2>", unsafe_allow_html=True)

# Smart Workflow Visual Prompt / Message Alert
if st.session_state.workflow_status == "awaiting_settlement":
    st.info("💡 **Next Step Needed:** Aapne profit process kar liya hai. Agar aap withdraw karna chahte hain to left side se amount bharein, nahi to seedhe **'🔄 Execute Settlements'** button par click karein taaki aapka naya active investment load ho sake!")
elif st.session_state.workflow_status == "settled_done":
    st.success("✅ **Settlement Complete:** Aapka agla cycle naye capital ke saath shuru hone ke liye taiyar hai!")
    st.session_state.workflow_status = "" # Flash message clear

# Top Bar Metrics Grid (4 Column Layout to include total withdrawals)
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("💼 Active Capital Base", f"${st.session_state.investment:.2f}")
with col_m2:
    st.metric("💰 Main Wallet Core Balance", f"${st.session_state.main_wallet:.2f}")
with col_m3:
    st.metric("🛡️ Support Wallet Rolling Base", f"${st.session_state.support_wallet:.2f}")
with col_m4:
    st.metric("💸 Total Withdrawn Amount", f"${st.session_state.total_withdrawn:.2f}")

st.write("---")

# Projection Analysis Block - EXACT MATCHING WITH LIVE LOGIC
days_list = [10, 15, 20, 25, 30, 35, 40]
pct_list = [15, 30, 50, 75, 100, 150, 200]

proj_data = []
temp_cap = st.session_state.initial_investment
virtual_main_wallet = 0.0
virtual_support_wallet = 0.0

for i in range(7):
    p_prof = (temp_cap * pct_list[i]) / 100
    m_share = temp_cap + (p_prof * 0.70)
    s_share = p_prof * 0.30
    
    virtual_main_wallet += m_share
    virtual_support_wallet += s_share
    
    # Perform strict settlement emulation
    main_round = int(virtual_main_wallet)
    virtual_main_wallet = virtual_main_wallet - main_round
    
    support_round = 0
    if virtual_support_wallet >= 10.0:
        support_round = int(virtual_support_wallet)
        virtual_support_wallet = virtual_support_wallet - support_round
        
    nxt_investment = float(main_round + support_round)
    
    proj_data.append({
        "Cycle Stage": cycle_names[i],
        "Duration": f"{days_list[i]} Days",
        "ROI": f"{pct_list[i]}%",
        "Expected Profit": f"${p_prof:.2f}",
        "Main Share (Post Cycle)": f"${m_share:.2f}",
        "Support Share (Post Cycle)": f"${s_share:.2f}",
        "Support Rollover Bal": f"${virtual_support_wallet:.2f}",
        "Perfect Reinvest Target": nxt_investment
    })
    temp_cap = nxt_investment

# Dynamic Impact Message Builder
max_theoretical_target = proj_data[-1]["Perfect Reinvest Target"]

# Calculate what the current live progression will reach if no more withdrawals occur
live_history_len = len(st.session_state.history)
current_live_investment = st.session_state.investment

# Run virtual engine starting from the user's CURRENT actual investment to the 7th cycle
simulated_cap = current_live_investment
sim_main_wallet = st.session_state.main_wallet
sim_support_wallet = st.session_state.support_wallet

for idx in range(live_history_len, 7):
    p_prof = (simulated_cap * pct_list[idx]) / 100
    m_share = simulated_cap + (p_prof * 0.70)
    s_share = p_prof * 0.30
    
    sim_main_wallet += m_share
    sim_support_wallet += s_share
    
    m_round = int(sim_main_wallet)
    sim_main_wallet = sim_main_wallet - m_round
    
    s_round = 0
    if sim_support_wallet >= 10.0:
        s_round = int(sim_support_wallet)
        sim_support_wallet = sim_support_wallet - s_round
        
    simulated_cap = float(m_round + s_round)

# The total loss calculation logic
potential_difference = max_theoretical_target - (simulated_cap + st.session_state.total_withdrawn)

# Dynamic Current Flow Sheet Table
st.subheader("📋 Active Lifecycle Statement (Live Steps Track)")
if st.session_state.history:
    df_history = pd.DataFrame(st.session_state.history)
    
    # Format the columns nicely
    df_display = df_history.copy()
    df_display["Profit Generated"] = df_display["Profit Generated"].map(lambda x: f"${x:.2f}")
    df_display["Withdrawal (Main)"] = df_display["Withdrawal (Main)"].map(lambda x: f"${x:.2f}")
    df_display["Support Auto Re-Invest"] = df_display["Support Auto Re-Invest"].map(lambda x: f"${x:.0f}")
    
    st.dataframe(df_display.set_index("Cycle"), use_container_width=True)
    
    # CLEAN & DYNMIC ANALYSIS DISPLAY
    if st.session_state.total_withdrawn > 0:
        st.markdown("### ⚠️ Compounding Opportunity Loss Report")
        if potential_difference > 0:
            st.warning(
                f"**Aapne abhi tak total `${st.session_state.total_withdrawn:.2f}` ka withdrawal kiya hai.**\n\n"
                f"Is withdrawal ki wajah se aapka compounding base chota ho gaya hai:\n"
                f"* 🎯 **Maximum Target (agar $ 0  withdraw karte): * `${int(max_theoretical_target)}` tak pahunchta.\n"
                f"* 📉 **Compounding Loss:** Aapne lagbhag `${int(potential_difference)}` ka extra profit miss kiya hai."
            )
        else:
            st.info("Aapka lifecycle statement bilkul track par hai.")
else:
    st.info("Pehle Left Sidebar se 'Complete Cycle & Process Profit' par click karein. Jaise-jaise aap aage badhenge, aapka real-time custom workflow yahan load hoga.")

st.write("---")

# Projection Analysis Block
st.subheader("🔮 Theoretical Compounding Map (If 0% Withdrawal Maintained From Start)")
st.caption(f"Fixed Map Base Calculation Level Set On Initial Entry: **${st.session_state.initial_investment:.2f}** (Calculated with identical decimal carry-overs as the live engine)")

# Adapt array presentation formatting for the view
df_proj = pd.DataFrame(proj_data)
df_proj["Perfect Reinvest Target"] = df_proj["Perfect Reinvest Target"].map(lambda x: f"${int(x)}")
st.table(df_proj.set_index("Cycle Stage"))
