import streamlit as st
import time
import json
import random
import pandas as pd
from datetime import datetime, timedelta
from multi_agent_system import run_pipeline

# =====================================================================
# 🏆 WARD OVERVIEW (VCC - NEW)
# =====================================================================
def render_ward_overview():
    """Renders a high-level summary of all ICU beds."""
    st.markdown("### 🏥 Virtual Command Center (Ward Overview)")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Patients", "12")
    with col2:
        st.metric("Critical Alerts", "1", delta="-1", delta_color="inverse")
    with col3:
        st.metric("High Risk", "2", delta="1", delta_color="normal")
    with col4:
        st.metric("System Uptime", "99.9%")
    st.markdown("---")

# =====================================================================
# 🎨 PREMIUM UI CONFIGURATION & THEME
# =====================================================================
st.set_page_config(
    page_title="GuardianAI: Elite CDS Monitor",
    page_icon="🛡️",
    layout="wide",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    .main { background-color: #05070A; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4 { font-family: 'Orbitron', sans-serif; letter-spacing: 1px; }
    .stApp { background-color: #05070A; }
    .glass-panel {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px; padding: 20px; backdrop-filter: blur(10px); margin-bottom: 20px;
    }
    .alarm-bg {
        background: linear-gradient(135deg, #450A0A 0%, #7F1D1D 100%);
        border: 2px solid #EF4444; box-shadow: 0 0 30px rgba(239, 68, 68, 0.3);
    }
    .warning-bg {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%);
        border: 2px solid #6366F1; box-shadow: 0 0 30px rgba(99, 102, 241, 0.3);
    }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #F8FAFC; margin: 0; }
    .metric-label { font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; }
    .pulse-alarm { animation: pulse-red 2s infinite; }
    @keyframes pulse-red {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { transform: scale(1.02); box-shadow: 0 0 0 15px rgba(239, 68, 68, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 🧠 SESSION STATE
# =====================================================================
if 'simulation_running' not in st.session_state: st.session_state.simulation_running = False
if 'current_time' not in st.session_state: st.session_state.current_time = 0
if 'history' not in st.session_state: st.session_state.history = []
if 'deterioration_onset' not in st.session_state: st.session_state.deterioration_onset = None
if 'actions_taken' not in st.session_state: st.session_state.actions_taken = []
if 'baseline_vitals' not in st.session_state:
    st.session_state.baseline_vitals = {
        "HR": 95, "SBP": 112, "MAP": 78, "O2Sat": 98, "Lactate": 1.5, 
        "Temp": 37.0, "Resp": 18, "WBC": 9000, "Platelets": 200, "Creatinine": 1.0
    }

def safe_rerun():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

# =====================================================================
# ⚙️ SIDEBAR (CONTROL PANEL)
# =====================================================================
with st.sidebar:
    st.markdown("<h2 style='color: #38BDF8;'>⚙️ CONTROL</h2>", unsafe_allow_html=True)
    st.subheader("1️⃣ Patient Setup")
    patient_id = st.text_input("Patient ID", "ICU-ALPHA-92")
    hr_init = st.number_input("Init HR", value=95)
    sbp_init = st.number_input("Init SBP", value=112)
    
    if st.button("SET BASELINE & START MONITORING"):
        st.session_state.baseline_vitals.update({"HR": hr_init, "SBP": sbp_init, "MAP": sbp_init*0.7})
        st.session_state.simulation_running = True
        st.session_state.current_time = 0
        st.session_state.history = []
        st.session_state.deterioration_onset = None
        st.session_state.actions_taken = []
        safe_rerun()

    st.write("---")
    st.subheader("2️⃣ Simulation Scenario")
    sim_path = st.selectbox("Scenario Path", ["Acute Onset", "Septic Shock", "Slow Drift", "Extreme Failure Case", "⚠️ Sensor Malfunction"])
    
    st.markdown("""
    <div style='margin-top: 20px; border-top: 1px solid #334155; padding-top: 15px;'>
        <p class='metric-label'>Model Info</p>
        <p style='font-size: 0.8rem; color: #CBD5E1;'>Type: XGBoost CDS Ensemble<br>Confidence: 94.2%</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.simulation_running:
        st.write("---")
        if st.button("🛑 STOP & RESET SIM"):
            st.session_state.simulation_running = False
            safe_rerun()

# =====================================================================
# 🏥 MAIN DASHBOARD
# =====================================================================
render_ward_overview() # 🏆 Winner Feature: VCC Ward Overview

st.markdown("""
<div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;'>
    <div>
        <h1 style='color: #38BDF8; margin: 0; font-size: 1.8rem;'>🛡️ GUARDIAN AI: ELITE</h1>
        <p style='color: #94A3B8; margin: 0; font-size: 0.8rem;'>Autonomous Clinical Decision System (CDS) • Simulated EMR Flow</p>
    </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.simulation_running:
    st.info("System Ready. Please initialize patient monitor in the sidebar to begin autonomous surveillance.")
else:
    dash_placeholder = st.empty()
    
    for t in range(st.session_state.current_time, 240, 1):
        st.session_state.current_time = t
        
        # Physics / Feedback Logic
        hr = st.session_state.baseline_vitals["HR"]
        sbp = st.session_state.baseline_vitals["SBP"]
        lac = st.session_state.baseline_vitals["Lactate"]
        resp = st.session_state.baseline_vitals["Resp"]
        
        # Treatment Agent Logic
        # risk = state.get("risk_level", "LOW")
        # vitals = state["vitals"] # Fixed key from 'patient_data' to 'vitals'
        
        if t >= 15:
            mult = 1.0
            if sim_path == "Acute Onset": mult = 1.5
            elif sim_path == "Septic Shock": mult = 3.5
            elif sim_path == "Extreme Failure Case": mult = 8.0
            elif sim_path == "Slow Drift": mult = 0.4
            
            # 🏆 Winner Feature: Sensor Malfunction Logic
            if sim_path == "⚠️ Sensor Malfunction":
                if t % 10 < 3: # Intermittent crazy spikes
                    hr = 250; sbp = 40; lac = 20.0 
            
            hr += (t-15) * 0.2 * mult
            sbp -= (t-15) * 0.15 * mult
            lac += (t-15) * 0.02 * mult
            resp += (t-15) * 0.05 * mult
            
            if "Antibiotics" in st.session_state.actions_taken:
                hr -= 0.2; sbp += 0.05; lac -= 0.01
            if "IV Fluids" in st.session_state.actions_taken:
                sbp += 0.3; hr -= 0.05
        
        hr += random.uniform(-0.5, 0.5)
        sbp += random.uniform(-0.3, 0.3)
        
        curr_data = {
            "HR": hr, "SBP": sbp, "MAP": sbp*0.7, "Lactate": max(0.5, lac),
            "O2Sat": 98 + random.uniform(-0.5, 0.5), "Temp": 37.0 + random.uniform(-0.05, 0.05),
            "Resp": max(12, resp), "WBC": 9000, "Platelets": 200, "Creatinine": 1.0,
            "antibiotics_given": "Antibiotics" in st.session_state.actions_taken,
        }
        
        result = run_pipeline(curr_data, st.session_state.history, st.session_state.deterioration_onset)
        struct = result["structured_output"]
        ui = result["ui_display"]
        
        if struct["deterioration_start_time"] and not st.session_state.deterioration_onset:
            st.session_state.deterioration_onset = struct["deterioration_start_time"]
        
        hist_entry = curr_data.copy()
        hist_entry['time'] = t; hist_entry['risk'] = result['risk_score']
        st.session_state.history.append(hist_entry)
        if len(st.session_state.history) > 60: st.session_state.history.pop(0)

        with dash_placeholder.container():
            # Banner
            alert_l = struct["alert"]["level"]
            banner_cls = "glass-panel"
            if alert_l == "CRITICAL": banner_cls += " alarm-bg pulse-alarm"
            elif alert_l == "HIGH": banner_cls += " warning-bg"
            
            st.markdown(f"""
            <div class='{banner_cls}'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div><p class='metric-label'>Simulation Time</p><h2>T + {t} MINS</h2></div>
                    <div style='text-align: center;'><h2 style='margin: 0;'>{ui['alert_banner']}</h2></div>
                    <div style='text-align: right;'><p class='metric-label'>Compliance Agent</p><h2>{ui['time_info']}</h2></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            cl1, cl2 = st.columns([1.5, 3])
            
            with cl1:
                st.markdown(f"""
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px;'>
                    <div class='glass-panel'><p class='metric-label'>Heart Rate</p><p class='metric-value'>{hr:.0f}</p></div>
                    <div class='glass-panel'><p class='metric-label'>SBP</p><p class='metric-value'>{sbp:.0f}</p></div>
                    <div class='glass-panel'><p class='metric-label'>Lactate</p><p class='metric-value'>{lac:.1f}</p></div>
                    <div class='glass-panel'><p class='metric-label'>Risk %</p><p class='metric-value'>{result['risk_score']:.1f}%</p></div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<div class='glass-panel'><h4 style='color: #38BDF8; font-size: 0.9rem;'>👨‍⚕️ Recommend Actions</h4>", unsafe_allow_html=True)
                if st.button("💉 Administer Antibiotics", key=f"abx_{t}"):
                    st.session_state.actions_taken.append("Antibiotics"); st.toast("Applying Antibiotics...")
                if st.button("💧 Start IV Fluids", key=f"iv_{t}"):
                    st.session_state.actions_taken.append("IV Fluids"); st.toast("Starting Fluids...")
                st.markdown("</div>", unsafe_allow_html=True)

            with cl2:
                df = pd.DataFrame(st.session_state.history)
                t1, t2 = st.tabs(["Vitals", "Risk Score"])
                with t1: st.line_chart(df[['HR', 'SBP', 'Lactate']], height=250)
                with t2: st.line_chart(df[['risk']], height=250)
            
            cx1, cx2 = st.columns([2, 1])
            with cx1:
                st.markdown(f"""
                <div class='glass-panel'>
                    <h4 style='color: #38BDF8; font-size: 0.9rem;'>🧠 Agent Reasoning</h4>
                    <p style='font-style: italic; color: #CBD5E1; font-size: 0.85rem; white-space: pre-wrap;'>{result['explanation']}</p>
                </div>
                """, unsafe_allow_html=True)
            with cx2:
                xai = struct["xai"]
                st.markdown(f"""
                <div class='glass-panel'>
                    <h4 style='color: #4ADE80; font-size: 0.9rem;'>📋 Protocol XAI</h4>
                    <p class='metric-label'>Rule</p><p style='font-size: 0.8rem;'>{xai['rule']}</p>
                    <p class='metric-label'>Time Window</p><p style='font-size: 0.8rem;'>{xai['window']}</p>
                </div>
                """, unsafe_allow_html=True)

            # --- 🏆 WINNER FEATURES: TREATMENT & INTEROP (NEW) ---
            c_row1, c_row2 = st.columns([1.5, 1])
            with c_row1:
                st.markdown(f"""
                <div class='glass-panel'>
                    <h4 style='color: #FACC15; font-size: 0.9rem;'>📋 Treatment Planner (Agent 8)</h4>
                    <p style='font-size: 0.75rem; color: #94A3B8;'><strong>Rationale</strong>: {result.get('clinical_rationale', 'Assessing...')}</p>
                """, unsafe_allow_html=True)
                for step in result.get('treatment_plan', []):
                    st.markdown(f"<p style='font-size: 0.8rem; margin: 0;'>{step}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with c_row2:
                st.markdown("""<div class='glass-panel'><h4 style='color: #60A5FA; font-size: 0.9rem;'>🧬 FHIR Interop</h4>""", unsafe_allow_html=True)
                with st.expander("View HL7 stream"):
                    st.json(result.get('fhir_payload', {}))
                st.markdown("</div>", unsafe_allow_html=True)

            # --- 🏆 WINNER FEATURES: SHIFT REPORT (NEW) ---
            with st.expander("📑 View GenAI End-of-Shift Handover Report (Agent 9)"):
                st.markdown(result.get('shift_summary', "Processing..."))

            with st.expander("🔍 System Audit Trail (Clinical Events)"):
                for entry in result["audit_trail"]:
                    st.markdown(f"<div style='font-family: monospace; font-size: 0.8rem; color: #38BDF8;'>{entry}</div>", unsafe_allow_html=True)
        
        time.sleep(0.4)
        if t == 239: st.session_state.simulation_running = False
