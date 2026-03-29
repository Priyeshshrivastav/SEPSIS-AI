from typing import List


def get_decision(data: dict, risk: float, alerts: List[str]) -> str:
    """
    HYBRID AI + RULE Decision System
    ──────────────────────────────────
    Priority order:
      1. Hard clinical safety rules  → ESCALATE  (non-negotiable)
      2. High AI risk (> 0.7)        → ESCALATE
      3. Moderate AI risk or ≥2 alerts → MONITOR CLOSELY
      4. Otherwise                   → STABLE
    """
    try:
        lactate = float(data.get("Lactate", 0.0))
        sbp     = float(data.get("SBP", 120.0))
    except (TypeError, ValueError):
        lactate = 0.0
        sbp = 120.0

    # ── Rule 1: Critical safety thresholds (always override AI score) ──
    if lactate > 3.0 or sbp < 90.0:
        return "ESCALATE"

    # ── Rule 2: AI score — high risk ──────────────────────────────────
    if risk > 0.7:
        return "ESCALATE"

    # ── Rule 3: Hybrid — moderate AI or multiple clinical flags ───────
    if risk > 0.4 or len(alerts) >= 2:
        return "MONITOR CLOSELY"

    # ── Rule 4: Stable ────────────────────────────────────────────────
    return "STABLE"


def generate_explanation(risk: float, alerts: List[str], decision: str) -> str:
    """
    Generates a human-readable, professional clinical explanation.
    Designed to demonstrate 'Explainable AI' for judges/PPT alignment.
    """
    risk_pct  = f"{risk:.0%}"
    risk_label = "high" if risk > 0.7 else "moderate" if risk > 0.4 else "low"
    parts: List[str] = []

    # 1. AI Risk Assessment
    parts.append(f"The AI risk model assigned a {risk_label} sepsis probability of {risk_pct}.")

    # 2. Clinical Marker Summary
    if alerts:
        # Strip parenthetical detail for readability
        readable = [a.split("(")[0].strip().lower() for a in alerts]
        if len(readable) == 1:
            marker_str = readable[0]
        else:
            marker_str = ", ".join(readable[:-1]) + f", and {readable[-1]}"
        parts.append(f"The clinical rule engine detected {len(alerts)} sepsis indicator(s): {marker_str}.")
    else:
        parts.append("No critical clinical threshold violations were detected by the rule engine.")

    # 3. Decision Rationale & Action Guidance
    if decision == "ESCALATE":
        parts.append(
            "Based on the combined AI + clinical rule assessment, IMMEDIATE ESCALATION is required. "
            "Initiate sepsis protocol: IV fluid resuscitation, broad-spectrum antibiotics within 1 hour, "
            "and continuous haemodynamic monitoring."
        )
    elif decision == "MONITOR CLOSELY":
        parts.append(
            "The patient is at intermediate risk. Close monitoring of vital signs and labs is essential. "
            "Reassess within 1 hour and escalate immediately if clinical status deteriorates."
        )
    else:
        parts.append(
            "Both the AI model and clinical rule engine indicate a stable state. "
            "Continue standard care and routine monitoring protocols."
        )

    return " ".join(parts)
