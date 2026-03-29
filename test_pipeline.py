"""
Sepsis AI — End-to-end pipeline test (no server required).
Run: python test_pipeline.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from model import load_model, prepare_input, predict_risk
from rules import evaluate_clinical_rules, add_critical_actions
from logic import get_decision, generate_explanation

# ── Critical test case (expected: ESCALATE, risk > 0.7) ──────────────────────
patient = {
    "HR":         125,
    "O2Sat":      90,
    "Temp":       39.0,
    "SBP":        85,
    "MAP":        60,
    "Resp":       28,
    "Lactate":    4.0,
    "WBC":        18000,
    "Platelets":  90000,
    "Creatinine": 2.5,
}

print("=" * 60)
print("SEPSIS AI — PIPELINE TEST")
print("=" * 60)
print("INPUT:", patient)

# 1. Feature prep
processed = prepare_input(patient)

# 2. ML prediction
model = load_model()
risk = predict_risk(model, processed)
print(f"ML RISK SCORE : {risk:.4f} ({risk:.1%})")

# 3. Clinical rules
alerts, actions = evaluate_clinical_rules(patient)
print(f"ALERTS [{len(alerts)}]  :", alerts)

# 4. Hybrid decision
decision = get_decision(patient, risk, alerts)
print(f"DECISION      : {decision}")

# 5. Final actions
final_actions = add_critical_actions(decision, risk, actions)
print(f"ACTIONS [{len(final_actions)}]  :", final_actions)

# 6. Explanation
explanation = generate_explanation(risk, alerts, decision)
print(f"\nEXPLANATION:\n{explanation}")

# ── Assertions ────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ASSERTIONS")
assert risk > 0.5,        f"FAIL: Risk too low ({risk:.2f}), expected > 0.5"
assert len(alerts) >= 3,  f"FAIL: Expected ≥3 alerts, got {len(alerts)}"
assert decision == "ESCALATE", f"FAIL: Expected ESCALATE, got {decision}"
print("✅  ALL ASSERTIONS PASSED — System is HACKATHON-READY")
print("=" * 60)
