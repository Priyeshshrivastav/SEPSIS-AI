"""
=======================================================================
GUARDIAN AI: ELITE  –  ICU Autonomous Monitoring & Compliance Engine
=======================================================================
Autonomous pipeline: 
  1. Data Validation (Sensor Check)
  2. Autonomous Deterioration Detection (Deterioration Start Time)
  3. Clinical Rule Override (ML Safety Layer)
  4. Protocol Compliance (Missed Intervention Detection)
  5. Multi-Agent Reasoning (Groq LLaMA-3)

Follows strict Hospital Clinical Decision System (CDS) principles.
=======================================================================
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict
from dotenv import load_dotenv

load_dotenv() # Load local .env if exists

# ── LangGraph / LangChain ──────────────────────────────────────────────
from langgraph.graph import END, StateGraph

try:
    from model import load_model, prepare_input, predict_risk
    _MODEL_AVAILABLE = True
except ImportError:
    _MODEL_AVAILABLE = False

# ── API Keys ─────────────────────────────────────────────────────────
# Pull from environment variables (.env locally or Streamlit Cloud Secrets)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    # If not found, use a placeholder or raise an error for developer safety
    print("WARNING: GROQ_API_KEY is not set! Using a local developer fallback for now.")
    GROQ_API_KEY = "dummy_v_0.1" # Using a placeholder for safe demo testing 


# ======================================================================
# STATE DEFINITION
# ======================================================================
class PatientState(TypedDict):
    patient_data: Dict[str, Any]
    history: List[Dict[str, Any]]
    
    # Validation
    sensor_error: bool
    validation_flags: List[str]

    # Detection
    deterioration_start_time: Optional[str]
    deterioration_triggers: List[str]

    # Analysis
    trend: str
    risk_level: str
    risk_score: float
    patient_status: str
    override_applied: bool

    # Compliance
    elapsed_time_minutes: float
    missing_actions: List[str]
    antibiotics_given: bool

    # Alert
    alert_level: str
    trigger_alarm: bool

    # AI Outputs
    explanation: str
    ui_alert_banner: str
    ui_patient_status: str
    ui_time_info: str
    ui_key_message: str
    ui_actions_required: List[str]
    
    # Winner Features (GenAI Expansion)
    treatment_plan: List[str]  # Agent 8: Suggested medical actions
    clinical_rationale: str     # Agent 8: Deep medical reasoning
    shift_summary: str          # Agent 9: End-of-shift handover report
    fhir_payload: dict          # FHIR/HL7 Interoperability data

    # Reasoning
    audit_trail: List[str]
    
    # XAI & Protocol
    protocol_name: str
    protocol_rule: str
    time_window: str


# ======================================================================
# AGENT 1: DATA VALIDATION AGENT
# ======================================================================
def validation_agent(state: PatientState) -> PatientState:
    """Enforces clinical realism for sensor data."""
    data = state["patient_data"]
    audit = list(state.get("audit_trail", []))
    flags = []
    error = False

    hr = float(data.get("HR", 0))
    sbp = float(data.get("SBP", 0))
    lac = float(data.get("Lactate", 0))

    if hr < 30 or hr > 220:
        flags.append(f"UNREALISTIC HR ({hr:.0f}): Possible sensor detachment or cardiac arrest.")
        error = True
    if sbp < 0 or sbp > 300:
        flags.append(f"UNREALISTIC BP ({sbp:.0f}): Check transducer/cuff calibration.")
        error = True
    if lac < 0 or lac > 30:
        flags.append(f"UNREALISTIC LACTATE ({lac:.1f}): Re-verify lab sample.")
        error = True

    if error:
        audit.append(f"[{_now()}] ⚠️ SENSOR ERROR: Unrealistic values detected. Conservative assessment engaged.")
    
    return {**state, "sensor_error": error, "validation_flags": flags, "audit_trail": audit}


# ======================================================================
# AGENT 2: DETECTION AGENT
# ======================================================================
def detection_agent(state: PatientState) -> PatientState:
    """Autonomously marks the exact second deterioration begins."""
    data = state["patient_data"]
    audit = list(state.get("audit_trail", []))
    
    hr = float(data.get("HR", 0))
    sbp = float(data.get("SBP", 120))
    map_val = float(data.get("MAP", 75))
    lac = float(data.get("Lactate", 0))

    triggers = []
    if hr > 100: triggers.append("Tachycardia (>100)")
    if sbp < 100 or map_val < 65: triggers.append("Hypotension (SBP<100/MAP<65)")
    if lac > 2.0: triggers.append("Hyperlactatemia (>2.0)")

    onset = str(state.get("deterioration_start_time") or "")
    if triggers and not onset:
        onset_time = datetime.now()
        onset = onset_time.isoformat()
        ts_str = onset_time.strftime("%H:%M")
        audit.append(f"{ts_str} → deterioration detected ({', '.join(triggers)})")
    else:
        onset = state.get("deterioration_start_time")
    
    return {**state, "deterioration_start_time": onset, "deterioration_triggers": triggers, "audit_trail": audit}


# ======================================================================
# AGENT 3: TREND AGENT
# ======================================================================
def trend_agent(state: PatientState) -> PatientState:
    """Evaluates stability trajectory."""
    curr = state["patient_data"]
    hist = state.get("history", [])
    if not hist: return {**state, "trend": "Baseline"}

    # Look back 5 time steps (or first if less than 5) to see the trend
    lookback = 5
    prev = hist[-min(len(hist), lookback)]
    trend = "Stable"
    
    hr_delta = float(curr.get("HR", 0)) - float(prev.get("HR", 0))
    sbp_delta = float(curr.get("SBP", 0)) - float(prev.get("SBP", 0))
    lac_delta = float(curr.get("Lactate", 0)) - float(prev.get("Lactate", 0))

    if hr_delta > 5 or sbp_delta < -5 or lac_delta > 0.2:
        trend = "Worsening"
    elif hr_delta < -5 and sbp_delta > 5 and lac_delta < -0.2:
        trend = "Improving"
        
    return {**state, "trend": trend}


# ======================================================================
# AGENT 4: CLINICAL OVERRIDE AGENT (MOST IMPORTANT)
# ======================================================================
def override_agent(state: PatientState) -> PatientState:
    """Overwrites ML output if clinical thresholds are extreme."""
    data = state["patient_data"]
    audit = list(state.get("audit_trail", []))
    
    # 1. Get ML score (baseline)
    score, level = _get_ml_assessment(data)
    override = False

    hr = float(data.get("HR", 0))
    sbp = float(data.get("SBP", 120))
    map_val = float(data.get("MAP", 75))
    lac = float(data.get("Lactate", 0))

    # 2. Strict Clinical Rules (FORCE CRITICAL)
    if lac > 4.0 or sbp < 80 or map_val < 55 or hr > 160:
        score = max(score, 0.98)
        level = "CRITICAL"
        override = True
        audit.append(f"[{_now()}] 🛠️ CLINICAL OVERRIDE: ML assessment ({score*100:.1f}%) bypassed due to extreme vitals. Risk set to CRITICAL.")
    elif lac > 2.5 or sbp < 95 or hr > 115:
        score = max(score, 0.65)
        level = "HIGH"
        override = True
        audit.append(f"[{_now()}] 🛠️ CLINICAL OVERRIDE: Vitals indicate HIGH risk despite model prediction.")

    # 3. Handle sensor error conservativism
    if state["sensor_error"] and level == "LOW":
        level = "MODERATE"
        score = 0.35
        audit.append(f"[{_now()}] 🛠️ CLINICAL OVERRIDE: Sensor error detected. Escalated risk for safety.")

    status = "STABLE"
    if level == "CRITICAL": status = "CRITICAL"
    elif level == "HIGH": status = "DETERIORATING"
    elif level == "MODERATE": status = "MONITOR"

    return {**state, "risk_score": score, "risk_level": level, "patient_status": status, "override_applied": override, "audit_trail": audit}


# ======================================================================
# AGENT 5: COMPLIANCE AGENT
# ======================================================================
def compliance_agent(state: PatientState) -> PatientState:
    """Tracks protocol execution vs time window."""
    onset = state.get("deterioration_start_time")
    data = state["patient_data"]
    audit = list(state.get("audit_trail", []))
    
    elapsed = 0.0
    missing = []
    failure = False

    if onset:
        if "time_since_detection" in data:
            elapsed = float(data["time_since_detection"])
        elif onset:
            try:
                onset_dt = datetime.fromisoformat(str(onset))
                elapsed = (datetime.now() - onset_dt).total_seconds() / 60.0
            except: pass

        abx = bool(data.get("antibiotics_given", False))
        fluids = bool(data.get("fluids_given", False))
        
        if elapsed > 60 and not abx:
            missing.append("Antibiotics not administered within 60 minutes (CRITICAL PROTOCOL VIOLATION)")
            failure = True
            audit.append(f"{_now_short()} → antibiotics delay detected ({elapsed:.0f} mins)")
        elif not abx:
            remaining = max(0, 60 - int(elapsed))
            missing.append(f"Administer antibiotics within {remaining} mins (SEP-1 window).")

    return {
        **state, 
        "elapsed_time_minutes": elapsed, 
        "missing_actions": missing, 
        "trigger_alarm": failure, 
        "audit_trail": audit,
        "protocol_name": "SEP-1 Sepsis Bundle",
        "protocol_rule": "IV Antibiotics & Fluids for Sepsis-3",
        "time_window": "60 Minutes from Onset"
    }


# ======================================================================
# AGENT 6: ALERT & UI AGENT
# ======================================================================
def ui_agent(state: PatientState) -> PatientState:
    """Prepares UI fields and final assessment."""
    level = state["risk_level"]
    status = state["patient_status"]
    elapsed = state["elapsed_time_minutes"]
    alarm = state["trigger_alarm"] or (level == "CRITICAL")
    
    alert_banner = "NORMAL MONITORING"
    if level == "CRITICAL": alert_banner = "🚨 CRITICAL ALARM: LIFE-THREATENING STATE"
    elif level == "HIGH": alert_banner = "⚠️ HIGH RISK: SEVERE DETERIORATION"

    key_msg = "Patient is stable."
    if state["sensor_error"]: key_msg = "POTENTIAL SENSOR ERROR. Re-check patient manually."
    elif alarm: key_msg = "CRITICAL INTERVENTION REQUIRED. Follow SEP-1 Bundle."
    elif status == "DETERIORATING": key_msg = "Patient trajectory is worsening. Increase monitoring."

    return {
        **state,
        "alert_level": level,
        "trigger_alarm": alarm,
        "ui_alert_banner": alert_banner,
        "ui_patient_status": status,
        "ui_time_info": f"T + {elapsed:.0f} MINS",
        "ui_key_message": key_msg,
        "ui_actions_required": state["missing_actions"],
    }


# ======================================================================
# AGENT 7: REASONING AGENT
# ======================================================================
def reasoning_agent(state: PatientState) -> PatientState:
    """Synthesises natural language explanation with explicit agent contributions."""
    agent_summary = (
        f"Prediction Agent: {state['risk_level']} Risk ({int(state['risk_score']*100)}%)\n"
        f"Trend Agent: {state['trend']}\n"
        f"Compliance Agent: {state['missing_actions'][0] if state['missing_actions'] else 'On Track'}\n"
        f"Alert Agent: {state['alert_level']} Alarm Triggered"
    )

    prompt = (
        f"Data Summary:\n{agent_summary}\n\n"
        f"Deterioration Onset: {state['deterioration_start_time']}\n"
        f"Elapsed: {state['elapsed_time_minutes']:.0f}m\n"
        f"Triggers: {state['deterioration_triggers']}\n"
        "Explain WHY the current alarm state exists. Focus on: "
        "1. Specific deterioration triggers. 2. Any protocol delays. 3. Immediate clinical requirements."
    )
    
    narrative = _groq_request(prompt)
    if not narrative:
        narrative = f"Alarm triggered due to {', '.join(state['deterioration_triggers'])}. " \
                    f"Compliance check: {state['missing_actions'][0] if state['missing_actions'] else 'Normal'}."

    final_explanation = f"{agent_summary}\n\nREASONING:\n{narrative}"

    return {**state, "explanation": final_explanation}


# ==========================================
# 🏆 AGENT 8: TREATMENT PLANNER (NEW)
# ==========================================
def treatment_planner_agent(state: PatientState):
    """Suggests specific medical interventions based on SEP-1 guidelines."""
    risk = state.get("risk_level", "LOW")
    vitals = state["patient_data"]
    
    plan = []
    rationale = ""
    
    if risk == "CRITICAL" or risk == "HIGH":
        # SEP-1 Bundle Logic
        plan.append("💉 Administer 30mL/kg IV Crystalloid Fluid bolus")
        plan.append("💊 Broad-spectrum Antibiotics (Vancomycin + Zosyn)")
        plan.append("🩸 Repeat Lactate measurement in 2 hours")
        if vitals.get("MAP", 70) < 65:
            plan.append("📈 Start Vasopressors (Norepinephrine) to maintain MAP > 65")
            rationale = "Patient is in decompensated septic shock with persistent hypotension."
        else:
            rationale = "Early aggressive fluid resuscitation indicated for sepsis-induced hypoperfusion."
    elif risk == "MODERATE":
        plan.append("🩸 Order Stat Blood Cultures x2")
        plan.append("🩺 Increase Vital monitoring frequency to every 15 mins")
        plan.append("🧪 Basic Metabolic Panel (BMP) to check renal function")
        rationale = "Localized infection likely; monitoring for systemic inflammatory response."
    else:
        plan.append("✅ Routine ICU monitoring")
        rationale = "Vitals within acceptable variance; no acute intervention needed."

    return {
        "treatment_plan": plan,
        "clinical_rationale": rationale
    }


# ==========================================
# 🏆 AGENT 9: SHIFT SUMMARY AGENT (NEW)
# ==========================================
def shift_summary_agent(state: PatientState):
    """Generates a professional handover report from the audit trail."""
    audit = state.get("audit_trail", [])
    if not audit:
        return {"shift_summary": "No clinical events recorded for this shift."}
    
    summary = f"### 📝 CLINICAL HANDOVER REPORT\n\n"
    summary += f"**Subject**: Patient Monitoring Shift Summary\n"
    summary += f"**Status**: {state.get('patient_status', 'Unknown')}\n\n"
    
    # Extract key events
    deterioration = [e for e in audit if "deterioration detected" in e]
    violations = [e for e in audit if "VIOLATION" in e]
    actions = [e for e in audit if "Action taken" in e]
    
    summary += "#### 🚨 Critical Events:\n"
    if deterioration:
        summary += f"- {deterioration[0]}\n"
    if violations:
        summary += f"- {violations[0]} (ALERT ESCALATED)\n"
    if not (deterioration or violations):
        summary += "- No critical deterioration events noted.\n"
        
    summary += "\n#### 💉 Interventions:\n"
    if actions:
        for a in actions: summary += f"- {a}\n"
    else:
        summary += "- Pending clinical interventions.\n"
        
    summary += "\n---\n*Generated by Guardian AI Intelligence Layer*"
    
    # Mock FHIR Payload for Interoperability Demo
    fhir = {
        "resourceType": "Observation",
        "status": "final",
        "category": [{"coding": [{"system": "http://hl7.org/fhir/observation-category", "code": "vital-signs"}]}],
        "code": {"text": "Sepsis Risk Assessment"},
        "subject": {"reference": "Patient/ICU-ALPHA-92"},
        "valueQuantity": {"value": state.get("risk_score", 0), "unit": "Probability"}
    }
    
    return {"shift_summary": summary, "fhir_payload": fhir}


# ======================================================================
# PIPELINE ORCHESTRATION
# ======================================================================
def build_graph():
    workflow = StateGraph(PatientState)
    workflow.add_node("validation", validation_agent)
    workflow.add_node("detection", detection_agent)
    workflow.add_node("trend", trend_agent)
    workflow.add_node("override", override_agent)
    workflow.add_node("compliance", compliance_agent)
    workflow.add_node("alert_ui", ui_agent)
    workflow.add_node("reasoning", reasoning_agent)
    workflow.add_node("treatment_planner", treatment_planner_agent)
    workflow.add_node("shift_summary", shift_summary_agent)

    # Build edges
    workflow.set_entry_point("validation")
    workflow.add_edge("validation", "detection")
    workflow.add_edge("detection", "trend")
    workflow.add_edge("trend", "override")
    workflow.add_edge("override", "compliance")
    workflow.add_edge("compliance", "alert_ui")
    workflow.add_edge("alert_ui", "reasoning")
    workflow.add_edge("reasoning", "treatment_planner")
    workflow.add_edge("treatment_planner", "shift_summary")
    workflow.add_edge("shift_summary", END)
    
    return workflow.compile()


def run_pipeline(data: Dict, history: List, onset_time: Optional[str] = None):
    initial = {
        "patient_data": data, "history": history, 
        "sensor_error": False, "validation_flags": [],
        "deterioration_start_time": onset_time, "deterioration_triggers": [],
        "trend": "Stable", "risk_level": "LOW", "risk_score": 0.0, "patient_status": "STABLE",
        "override_applied": False, "elapsed_time_minutes": 0.0, "missing_actions": [],
        "antibiotics_given": bool(data.get("antibiotics_given", False)),
        "alert_level": "LOW", "trigger_alarm": False,
        "ui_alert_banner": "", "ui_patient_status": "", "ui_time_info": "", "ui_key_message": "", "ui_actions_required": [],
        "explanation": "", "audit_trail": [f"[{_now()}] 🏁 Pipeline Cycle Started."],
        "treatment_plan": [], "clinical_rationale": "", "shift_summary": "", "fhir_payload": {},
        "protocol_name": "", "protocol_rule": "", "time_window": ""
    }
    
    graph = build_graph()
    res = graph.invoke(initial)
    
    return {
        "structured_output": {
            "deterioration_start_time": res["deterioration_start_time"],
            "elapsed_time_minutes": round(res["elapsed_time_minutes"], 1),
            "trend": res["trend"],
            "risk_level": res["risk_level"],
            "patient_status": res["patient_status"],
            "missing_actions": res["missing_actions"],
            "alert": {
                "level": res["alert_level"],
                "trigger_alarm": res["trigger_alarm"]
            },
            "xai": {
                "protocol": res["protocol_name"],
                "rule": res["protocol_rule"],
                "window": res["time_window"]
            }
        },
        "ui_display": {
            "alert_banner": res["ui_alert_banner"],
            "patient_status": res["ui_patient_status"],
            "time_info": res["ui_time_info"],
            "key_message": res["ui_key_message"],
            "actions_required": res["ui_actions_required"]
        },
        "risk_score": round(res["risk_score"] * 100, 1), 
        "explanation": res["explanation"],
        "audit_trail": res["audit_trail"],
        "treatment_plan": res["treatment_plan"],
        "clinical_rationale": res["clinical_rationale"],
        "shift_summary": res["shift_summary"],
        "fhir_payload": res["fhir_payload"]
    }


# ======================================================================
# INTERNAL HELPERS
# ======================================================================
def _now(): return datetime.now().strftime("%H:%M:%S")
def _now_short(): return datetime.now().strftime("%H:%M")

def _get_ml_assessment(data):
    if _MODEL_AVAILABLE:
        try:
            model = load_model()
            inp = prepare_input(data)
            score = predict_risk(model, inp)
        except: score = 0.1
    else: score = 0.1
    
    level = "LOW"
    if score > 0.8: level = "CRITICAL"
    elif score > 0.6: level = "HIGH"
    elif score > 0.3: level = "MODERATE"
    return score, level

def _groq_request(prompt):
    import requests
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        body = {"model": "llama3-8b-8192", "messages": [{"role": "system", "content": prompt}], "temperature": 0.1}
        r = requests.post(url, headers=headers, json=body, timeout=5)
        return r.json()["choices"][0]["message"]["content"].strip()
    except: return None
