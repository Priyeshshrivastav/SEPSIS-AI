import json
import time
from datetime import datetime

# =====================================================================
# AGENT DEFS
# =====================================================================

def prediction_agent(state):
    """Predicts risk via ML thresholds."""
    lactate = state['current_vitals'].get('Lactate', 1.0)
    sbp = state['current_vitals'].get('SBP', 120)
    
    # Heuristic for ML risk score
    risk_score = min(0.15 + (lactate * 0.1) + (0.2 if sbp < 100 else 0), 0.99)
    risk_level = "HIGH" if risk_score > 0.6 else "MODERATE" if risk_score > 0.3 else "LOW"
    
    return {"risk_score": f"{risk_score*100:.1f}%", "risk_level": risk_level}


def clinical_agent(state):
    """Applies strict medical rules."""
    vitals = state['current_vitals']
    alerts = []
    if vitals.get('HR', 0) > 100: alerts.append("Tachycardia")
    if vitals.get('SBP', 120) < 100 or vitals.get('MAP', 70) < 65: alerts.append("Hypotension")
    if vitals.get('Lactate', 0) > 2.0: alerts.append("High risk: Lactate > 2")
    return alerts


def trend_agent(state):
    """Detects directionality over time."""
    if not state.get('history'): 
        return "Stable"
    
    past = state['history'][-1]
    curr = state['current_vitals']
    
    if curr.get('Lactate', 0) > past.get('Lactate', 0) + 0.4 or curr.get('SBP', 120) < past.get('SBP', 120) - 5:
        return "Worsening"
    elif curr.get('Lactate', 10) < past.get('Lactate', 0) - 0.4:
        return "Improving"
        
    return "Stable"


def compliance_agent(state):
    """Tracks time delays and inaction."""
    missing = []
    status = "COMPLIANT"
    detected_mins = state['time_since_detection']
    
    if detected_mins > 60 and not state['antibiotics_given']:
        missing.append(f"CRITICAL DELAY: Antibiotics not given within 1 hour! (T+{detected_mins}m)")
        status = "VIOLATION"
    elif detected_mins > 0 and not state['antibiotics_given']:
        missing.append(f"Pending: Antibiotics needed in {max(0, 60 - detected_mins)} mins")
        
    return missing, status


def alert_agent(state, trend, clinical, compliance_status):
    """Decides if alarms must be fired."""
    # CRITICAL WINNING LOGIC: Worsening + Lactate + Inaction
    if trend == "Worsening" and any("Lactate" in c for c in clinical) and compliance_status == "VIOLATION":
        return {
            "alert_level": "CRITICAL", 
            "alert_message": "CRITICAL: Patient deteriorating + no intervention", 
            "trigger_alarm": True
        }
    elif trend == "Worsening" or len(clinical) >= 2:
        return {
            "alert_level": "WARNING", 
            "alert_message": "Suggest immediate monitoring", 
            "trigger_alarm": False
        }
        
    return {
        "alert_level": "NORMAL", 
        "alert_message": "Patient stable", 
        "trigger_alarm": False
    }


def reasoning_agent(pred, clinical, trend, compliance, alert):
    """Resolves conflicts and generates decision + actions."""
    if alert['trigger_alarm']:
        status = "CRITICAL"
        issue = "MISSED LIFE-SAVING ACTION: Deterioration without antibiotic intervention"
        actions = ["EMERGENCY ESCALATION", "Administer Antibiotics IMMEDIATELY", "Call Rapid Response"]
        
    elif alert['alert_level'] == "WARNING":
        status = "DETERIORATING"
        issue = "Deteriorating trend with abnormal vitals"
        actions = ["Increase monitoring frequency", "Prepare IV antibiotics"]
        
    else:
        status = "STABLE"
        issue = "Vitals within acceptable limits"
        actions = ["Continue standard ICU monitoring"]
        
    # Example explicitly overriding ML
    if pred['risk_level'] == "LOW" and trend == "Worsening":
         issue = "Trend analysis OVERRODE ML Prediction: Worsening status active."
         status = "MONITOR"
         
    return {"patient_status": status, "key_issue": issue, "recommended_actions": actions}


# =====================================================================
# ORCHESTRATOR
# =====================================================================

def run_icu_time_step(patient_state, current_min):
    audit_trail = []
    def log(msg): audit_trail.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    log(f"Initiating evaluation for T+{current_min}m.")
    
    pred = prediction_agent(patient_state)
    log(f"Prediction Agent computed risk: {pred['risk_level']}")
    
    clin = clinical_agent(patient_state)
    log(f"Clinical Agent identified {len(clin)} abnormalities.")
    
    trend = trend_agent(patient_state)
    log(f"Trend Agent detected trajectory: {trend}")
    
    comp, comp_status = compliance_agent(patient_state)
    log(f"Compliance Agent status: {comp_status}")
    
    alert = alert_agent(patient_state, trend, clin, comp_status)
    if alert['trigger_alarm']: 
        log(f"Alert Agent FIRED ALARM: OVERRIDE active due to inaction.")
    
    reason = reasoning_agent(pred, clin, trend, comp, alert)
    log(f"Reasoning Agent finalized status: {reason['patient_status']}")

    return {
        "timestamp": f"T+{current_min} mins",
        "agent_outputs": {
            "prediction_agent": pred,
            "clinical_agent": clin,
            "trend_agent": trend,
            "compliance_agent": comp,
            "alert_agent": alert
        },
        "final_decision": reason,
        "audit_trail": audit_trail
    }


# =====================================================================
# SIMULATION LOOP (Real-time tracking)
# =====================================================================

if __name__ == "__main__":
    
    print("\n========================================================")
    print("🏥 ICU REAL-TIME AUTONOMOUS SEPSIS MONITORING SIMULATION")
    print("========================================================\n")
    
    # 3 distinct times showing inaction and deterioration
    timeline = [
        {"time": 0,  "vitals": {"HR": 95,  "SBP": 110, "MAP": 75, "Lactate": 1.5}, "antibiotics": False, "detected": 0},
        {"time": 30, "vitals": {"HR": 110, "SBP": 95,  "MAP": 66, "Lactate": 2.5}, "antibiotics": False, "detected": 30},
        {"time": 65, "vitals": {"HR": 125, "SBP": 85,  "MAP": 55, "Lactate": 4.0}, "antibiotics": False, "detected": 65} # Over 1 hr!
    ]
    
    state = {"history": [], "current_vitals": {}, "antibiotics_given": False, "time_since_detection": 0}
    
    for snapshot in timeline:
        time.sleep(1) # Dramatic real-time pause for demonstration
        
        # Load snapshot into shared state
        state['current_vitals'] = snapshot['vitals']
        state['antibiotics_given'] = snapshot['antibiotics']
        state['time_since_detection'] = snapshot['detected']
        
        # Agents Process State
        result = run_icu_time_step(state, snapshot['time'])
        
        # Print perfectly formatted nested JSON
        print(f"\n▼ --- LIVE EMR FEED: TIMESTEP T+{snapshot['time']} Minutes --- ▼")
        print(json.dumps(result, indent=2))
        
        # Engine updates history for next loop
        state['history'].append(snapshot['vitals'].copy())
