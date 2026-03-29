from typing import List, Tuple

def evaluate_clinical_rules(data: dict) -> Tuple[List[str], List[str]]:
    """
    Clinical Alerts Engine
    Detects critical sepsis markers and returns alerts + initial suggested actions.
    Thresholds are aligned with Sepsis-3 / SIRS criteria.
    """
    alerts: List[str] = []
    suggested_actions: List[str] = []

    # HR > 100 → Tachycardia  (SIRS criterion)
    hr = float(data.get('HR', 0))
    if hr > 100:
        alerts.append("Tachycardia (HR > 100 bpm)")

    # SBP < 90 → Hypotension  (Septic shock marker)
    sbp = float(data.get('SBP', 120))
    if sbp < 90:
        alerts.append("Hypotension (SBP < 90 mmHg)")
        _add_unique(suggested_actions, "Start IV fluids (30 mL/kg bolus)")

    # Resp > 22 → Tachypnea  (SIRS criterion)
    resp = float(data.get('Resp', 0))
    if resp > 22:
        alerts.append("Tachypnea (Resp Rate > 22 br/min)")

    # Lactate > 2 → Hyperlactatemia  (tissue hypoperfusion)
    lactate = float(data.get('Lactate', 0))
    if lactate > 2:
        alerts.append("Hyperlactatemia (Lactate > 2 mmol/L)")

    # WBC > 12000 → Leukocytosis  (infection signal)
    wbc = float(data.get('WBC', 0))
    if wbc > 12000:
        alerts.append("Leukocytosis — Infection Signal (WBC > 12,000 cells/µL)")

    # O2Sat < 94 → Hypoxaemia
    o2sat = float(data.get('O2Sat', 100))
    if o2sat < 94:
        alerts.append(f"Hypoxaemia (O₂ Sat {o2sat}% < 94%)")

    return alerts, suggested_actions


def add_critical_actions(decision: str, risk: float, suggested_actions: List[str]) -> List[str]:
    """
    Appends evidence-based actions based on final decision + risk level.
    Order is preserved (clinically meaningful priority).
    """
    if decision == "ESCALATE":
        _add_unique(suggested_actions, "Start IV fluids (30 mL/kg bolus)")
        _add_unique(suggested_actions, "Administer broad-spectrum antibiotics within 1 hour")
        _add_unique(suggested_actions, "Monitor serum lactate (repeat in 2 hrs)")
        _add_unique(suggested_actions, "Blood cultures x2 before antibiotics")
        _add_unique(suggested_actions, "Notify ICU / Rapid Response Team")

    elif decision == "MONITOR CLOSELY":
        _add_unique(suggested_actions, "Frequent vitals monitoring (every 15–30 mins)")
        _add_unique(suggested_actions, "Reassess clinical status in 1 hour")
        _add_unique(suggested_actions, "Ensure IV access is available")

    return suggested_actions  # preserve insertion order (no set())


def _add_unique(lst: List[str], item: str):
    """Append item to list only if not already present (order-preserving dedup)."""
    if item not in lst:
        lst.append(item)
