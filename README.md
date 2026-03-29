# 🛡️ Guardian AI: Real-Time Sepsis Monitoring & Escalation Intelligence

> **Hackathon Project** — An autonomous, multi-agent Clinical Decision Support (CDS) system that doesn't just predict sepsis risk — it watches for **delayed treatment** and triggers escalation when clinicians fail to act in time.

---

## 💡 Motivation

Sepsis is a **life-threatening medical emergency** caused by the body's extreme response to infection. It is one of the leading causes of death in intensive care units globally, killing an estimated **11 million people every year** — roughly 20% of all global deaths.

The tragedy is not that we lack the tools to detect it. Modern medicine has highly effective early-warning systems, early-alert scores, and AI risk models. The tragedy is what happens **after** those warnings are issued.

> **"Clinicians are overloaded. Alert fatigue is real. And every minute of delay in antibiotic administration increases mortality by 7%."**
> — *Kumar et al., Critical Care Medicine*

Guardian AI was built from a simple, urgent observation: **detection without enforcement is insufficient.** A system that raises an alert and then waits passively for human action is failing at the most critical moment. We were motivated to build something that holds the entire care chain accountable — not just the patient's body.

This project was also motivated by the **SEP-1 Quality Measure** enforced by the Centers for Medicare & Medicaid Services (CMS), which requires IV antibiotics and fluid resuscitation within **one hour** of sepsis presentation. Hospitals routinely fail this benchmark not because they lack knowledge, but because there is no autonomous system that *enforces* it in real-time.

---

## 🎯 Need

### Why Current Systems Are Not Enough

Despite advances in clinical AI, a critical gap remains — the **clinical inaction window**:

| Gap | Description |
|---|---|
| **Alert Fatigue** | Clinical staff receive hundreds of alerts per shift; many are dismissed or delayed |
| **No Time Enforcement** | Existing tools flag risk but do not autonomously track elapsed time post-detection |
| **No Accountability Layer** | When a protocol is missed, there is no system-generated record of the delay |
| **Passive AI** | Most ML models are one-shot predictors — they don't *monitor* the follow-through |
| **Siloed Decisions** | Risk prediction and antibiotic administration are tracked in separate systems with no link |

### Who Needs This System

- 🏥 **ICU clinicians and nurses** — need an autonomous watchdog that escalates what humans miss during busy shifts
- 🩺 **Hospital quality officers** — need automated SEP-1 bundle compliance tracking and audit evidence
- 🧑‍💼 **Hospital administrators** — face CMS penalties for SEP-1 non-compliance; need provable time-stamped records
- 🔬 **Healthcare AI researchers** — need a reference implementation showing how multi-agent systems can enforce clinical protocols
- 🎓 **Medical educators** — can use this as a simulation tool to teach sepsis protocol adherence

### The Core Need in One Sentence

> **Healthcare systems need an AI that doesn't just predict deterioration — it needs to detect, time, track, and escalate when the human response fails to follow through.**

Guardian AI directly addresses this need with an autonomous 7-agent pipeline that treats **delayed intervention as a detectable clinical event**, not a passive miss.

---

## 🎯 1 - OBJECTIVES

The primary objective of Guardian AI is to bridge the "Silent Gap" in sepsis care by transforming a passive monitoring tool into an active clinical protocol enforcer.

*   **Real-Time Detection**: Continuously monitor ICU patient vitals (HR, SBP, Lactate, etc.) to detect physiological deterioration the moment it begins.
*   **Autonomous Compliance Tracking**: Automatically initiate a 60-minute countdown (per SEP-1 guidelines) upon detection of sepsis criteria.
*   **Clinical Accountability**: Monitor for specific clinical interventions (e.g., antibiotic administration) and trigger high-level escalation if actions are not taken within the protocol window.
*   **Explainable Reasoning**: Provide clinicians with real-time, human-readable explanations of *why* an alert was triggered and *what* specific actions are overdue.
*   **End-to-End Auditability**: Maintain a secure, timestamped record of every patient deterioration, system alert, and clinician response for quality review and legal compliance.

---

## 📚 2 - LITERATURE REVIEW

Traditional Sepsis Alerting Systems (SAS) have focused heavily on **prediction accuracy** while overlooking **clinical response implementation**.

1.  **The SEP-1 Mandate**: The Centers for Medicare & Medicaid Services (CMS) introduced the SEP-1 bundle, requiring completion of specific tasks (lactate measurement, blood cultures, antibiotics, and fluid bolus) within 3 to 6 hours. Studies show that **compliance with the 1-hour "Golden Hour"** significantly reduces mortality.
2.  **Alert Fatigue Challenge**: Research indicates that clinicians overlook up to **80-90% of automated alerts** due to high volume and poor specificity. This "noise" often leads to delayed treatment even when the AI correctly predicts sepsis.
3.  **Human Factors in Healthcare**: Psychological studies on clinical environments highlight that during high-stress ICU shifts, "omission errors" (failing to do something) are more common than "commission errors" (doing the wrong thing).
4.  **Multi-Agent Systems (MAS) in Medicine**: Recent literature suggests that MAS architectures are better suited for clinical environments because they allow for modular responsibility—where one agent validates data, another predicts risk, and a third enforces protocols—mirroring the collaborative nature of a medical team.

---

## 🧠 3 - SYSTEM INTELLIGENCE

Guardian AI utilizes a **Hybrid Intelligence Architecture** that combines Machine Learning with Clinical Rule Engines and Large Language Models.

*   **Predictive Intelligence**: A gradient-boosted decision tree (**XGBoost**) identifies subtle patterns in vital signs that precede septic shock, providing a probability score for sepsis onset.
*   **Deteriorative Timer (Stateful Intelligence)**: Using **LangGraph**, the system maintains a persistent "Patient State" that records the exact micro-second deterioration begins. This allows the system to remain "aware" of time passing, even across different cycles.
*   **Clinical Safety Governor**: A rule-based engine that acts as a "hard-stop" safeguard. If vitals reach critical thresholds (e.g., SBP < 80), the system overrides the ML model to ensure a CRITICAL alarm is triggered regardless of the model's confidence.
*   **LLM Cognitive Reasoning**: **Groq-powered LLaMA-3** agents synthesize the outputs of all clinical agents to generate a narrative. Instead of just showing a "90%" score, the system says: *"Sepsis suspected due to rising Shock Index (1.1) and high Lactate (2.5). Antibiotic window expires in 12 minutes—immediate intervention required."*

---

## 📊 4 - DATASET DESCRIPTION

The intelligence of Guardian AI is built upon large-scale clinical data and high-fidelity simulations.

*   **Training Source**: The underlying XGBoost model was trained on the **PhysioNet/Computing in Cardiology Challenge 2019** dataset, which contains over 40,000 ICU patients from two separate hospital systems.
*   **Simulated Real-Time Feed**: For the simulation dashboard, we developed a **Clinical Physics Engine** that models four distinct patient trajectories:
    *   **Acute Onset**: Rapid decline in vitals within 15-30 minutes.
    *   **Slow Drift**: Subtle deterioration over several hours.
    *   **Extreme Failure**: Immediate life-threatening vital collapse.
    *   **Septic Shock**: Classic presentation with hypotension and hyperlactatemia.
*   **Validation Set**: The system was tested against known clinical scenarios to ensure the **Detection Agent** triggers within ±2 minutes of standard Sepsis-3 clinical criteria.

---

## 🧬 5 - FEATURES USED

Guardian AI processes a specific set of raw and derived features to maintain high sensitivity to septic deterioration.

### Raw Vitals (Dynamic)
*   **HR (Heart Rate)**: Essential for detecting tachycardia.
*   **SBP (Systolic Blood Pressure)**: Critical for identifying hypotension.
*   **MAP (Mean Arterial Pressure)**: The primary indicator of organ perfusion.
*   **Lactate**: The biochemical marker for tissue hypoperfusion and metabolic stress.
*   **O2Sat**: Oxygen saturation for respiratory assessment.
*   **Temp**: To monitor for febrile or hypothermic responses to infection.

### Derived Clinical Features
*   **Shock Index (HR / SBP)**: A powerful early indicator of circulatory collapse, often more sensitive than blood pressure alone.
*   **MAP-Lactate Ratio**: Correlates strongly with the severity of septic shock.
*   **Trend Deltas (Last 15m)**: Calculated by the **Trend Agent** to determine the *velocity* of deterioration (Stable vs. Worsening).
*   **Compliance Timer**: A temporal feature representing minutes elapsed since the *Detection Agent* first recorded a protocol breach.

---

## 🚨 The Problem: The Silent Gap in Sepsis Care

Every year, sepsis kills millions of patients worldwide. Most hospitals have early-warning systems. So why are patients still dying?

**The answer is not detection — it's inaction after detection.**

| What Existing Systems Do | What Guardian AI Does |
|---|---|
| ✅ Flags rising vitals | ✅ Flags rising vitals |
| ✅ Predicts sepsis probability | ✅ Predicts sepsis probability |
| ❌ Cannot tell if treatment happened | ✅ Checks if antibiotics were given within 60 min |
| ❌ Stays silent if doctors ignore alerts | ✅ Triggers a **CRITICAL alarm** if no intervention occurs |
| ❌ No time-based escalation | ✅ Autonomous timer runs from the moment deterioration begins |
| ❌ No audit trail | ✅ Full clinical event log with timestamps |

> **The "Silent Gap"**: A patient deteriorates. The monitor beeps. The team is busy. An hour passes. No antibiotics. The patient crashes. Guardian AI closes this gap by treating **inaction** as a violation — and responding accordingly.

---

## 🧠 What We Built

A **real-time, autonomous, multi-agent AI system** that monitors ICU patients, detects physiological deterioration, enforces the SEP-1 clinical bundle compliance window, and triggers intelligible, explainable escalation alarms — entirely without human initiation.

**The key innovation**: Guardian AI autonomously starts a 60-minute countdown the moment deterioration criteria are met, then checks whether antibiotics have been administered. If not — it escalates with a critical alarm, sound notification, and a full audit trail — regardless of whether any human noticed.

---

## ✨ Core Features

- 🔴 **ML-Based Risk Prediction** — XGBoost model trained on clinical vitals (HR, SBP, MAP, Lactate, O₂Sat, WBC, etc.)
- 🕐 **Autonomous Deterioration Timer** — Records the exact timestamp when deterioration begins; no manual input needed
- 💊 **SEP-1 Bundle Compliance Tracking** — Monitors whether antibiotics were administered within the 60-minute protocol window
- 🚨 **Critical Alarm & Visual Banner** — Pulsing red alarm with animated banner on protocol violation
- 🤖 **7-Agent Autonomous Pipeline** — Each agent has a single responsibility and hands off state to the next
- 🧬 **Clinical Rule Override Engine** — Hard-coded clinical safety rules override ML predictions when vitals are extreme
- 📋 **XAI Protocol Panel** — Shows which rule triggered the alert and why, in plain language
- 🔍 **Full Audit Trail** — Timestamped event log of every clinical decision made by the system
- 📈 **Live Vital Trend Charts** — Real-time HR, SBP, Lactate, and Risk Score graphs
- 💬 **LLM-Powered Reasoning** — Groq LLaMA-3 generates a human-readable explanation for every alarm state

---

## 🏗️ Project Architecture

```
Patient Vital Stream (Simulated EMR / ICU feed)
             │
             ▼
   ┌─────────────────────┐
   │  Data Validation    │  ← Sensors checked for realism; flags detachment/
   │  Agent              │    calibration errors before any clinical logic runs
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  Detection Agent    │  ← Compares vitals against Sepsis-3 / SIRS criteria;
   │                     │    records exact ISO timestamp when deterioration begins
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  Trend Agent        │  ← Looks back 5 time steps; classifies trajectory
   │                     │    as Worsening / Stable / Improving
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  Clinical Override  │  ← Hard clinical thresholds override ML output for
   │  Agent              │    extreme vitals (Lactate >4, SBP <80, HR >160)
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  Compliance Agent   │  ← Calculates elapsed time from deterioration onset;
   │  (SEP-1 Enforcer)   │    checks antibiotic administration; flags violations
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  Alert & UI Agent   │  ← Prepares dashboard state: banner text, alarm class,
   │                     │    key message, and required actions for display
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  Reasoning Agent    │  ← Calls Groq LLaMA-3 to generate narrative explanation;
   │  (LLM + Audit)      │    appends all decisions to the clinical audit trail
   └──────────┬──────────┘
              │
              ▼
     Streamlit Dashboard
   (Real-time ICU Monitor)
```

---

## 🤖 Multi-Agent Workflow

The pipeline is built with **LangGraph** (`StateGraph`). All agents share a typed `PatientState` dictionary. Each agent reads from it and writes back updated fields, then passes state to the next node.

### Agent 1 — Validation Agent
| | |
|---|---|
| **Input** | Raw patient vitals dict (HR, SBP, Lactate, etc.) |
| **Output** | `sensor_error: bool`, `validation_flags: List[str]` |
| **Logic** | If HR < 30 or > 220, SBP < 0 or > 300, or Lactate < 0 or > 30 → flags unrealistic sensor reading and sets conservative mode |
| **Passes to** | Detection Agent |

### Agent 2 — Detection Agent
| | |
|---|---|
| **Input** | Validated vitals, existing `deterioration_start_time` |
| **Output** | `deterioration_start_time: ISO timestamp`, `deterioration_triggers: List[str]` |
| **Logic** | If HR > 100, SBP < 100, MAP < 65, or Lactate > 2.0 detected **and** no onset time exists → records exact ISO timestamp. Idempotent — will not overwrite an existing onset time. |
| **Passes to** | Trend Agent |

### Agent 3 — Trend Agent
| | |
|---|---|
| **Input** | Current vitals + last 5 historical readings |
| **Output** | `trend: "Worsening" | "Stable" | "Improving"` |
| **Logic** | Computes delta for HR, SBP, Lactate over last 5 steps. If HR↑5+, SBP↓5+, or Lactate↑0.2+ → Worsening. All three reversed → Improving. |
| **Passes to** | Clinical Override Agent |

### Agent 4 — Clinical Override Agent
| | |
|---|---|
| **Input** | ML risk score, current vitals, sensor error flag |
| **Output** | `risk_score`, `risk_level`, `patient_status`, `override_applied` |
| **Logic** | Calls XGBoost model as baseline. If Lactate > 4.0, SBP < 80, MAP < 55, or HR > 160 → **force CRITICAL (override)**. If Lactate > 2.5, SBP < 95, or HR > 115 → **force HIGH**. Sensor error with LOW prediction → escalate to MODERATE. |
| **Passes to** | Compliance Agent |

### Agent 5 — Compliance Agent *(Core Innovation)*
| | |
|---|---|
| **Input** | `deterioration_start_time`, `antibiotics_given` flag, current vitals |
| **Output** | `elapsed_time_minutes`, `missing_actions`, `trigger_alarm` |
| **Logic** | Calculates elapsed minutes from onset. If elapsed > 60 **and** no antibiotics given → sets `trigger_alarm = True`, appends protocol violation to audit trail. If within window → shows remaining minutes. |
| **Protocol** | SEP-1 Bundle: IV Antibiotics & Fluids within 60 minutes of Sepsis-3 criteria |
| **Passes to** | Alert Agent |

### Agent 6 — Alert & UI Agent
| | |
|---|---|
| **Input** | `risk_level`, `patient_status`, `trigger_alarm`, `missing_actions`, `elapsed_time_minutes` |
| **Output** | `ui_alert_banner`, `ui_patient_status`, `ui_time_info`, `ui_key_message`, `ui_actions_required` |
| **Logic** | Maps system state to display-ready strings. CRITICAL state → red pulsing banner. HIGH → indigo warning panel. Prepares concise key message for clinician in one line. |
| **Passes to** | Reasoning Agent |

### Agent 7 — Reasoning Agent
| | |
|---|---|
| **Input** | Full agent summary (risk, trend, compliance status, alarm level) + deterioration context |
| **Output** | `explanation` (formatted agent summary + LLM narrative), updated `audit_trail` |
| **Logic** | Constructs a structured prompt from all agent outputs and calls **Groq LLaMA-3 (llama3-8b-8192)**. If API unavailable → falls back to deterministic explanation. Writes final narrative to audit trail. |

---

## ⏱️ Real-Time Monitoring Logic

### How Deterioration Is Detected

The **Detection Agent** checks every incoming data frame against Sepsis-3 / SIRS criteria:

```python
if HR > 100:      → Tachycardia
if SBP < 100 or MAP < 65:  → Hypotension
if Lactate > 2.0: → Hyperlactatemia (tissue hypoperfusion)
```

When **any criterion** is met for the first time, the agent records the exact timestamp:
```python
onset_time = datetime.now().isoformat()  # e.g. "2026-03-28T19:13:00.423162"
```

### How the Timer Starts Automatically

The onset timestamp is stored in shared `PatientState`. It is **never overwritten** once set (idempotent). Every subsequent pipeline cycle passes this value forward so all downstream agents always know when deterioration began.

### How Delay Is Detected

The **Compliance Agent** computes:
```python
elapsed = (datetime.now() - onset_datetime).total_seconds() / 60.0
```
If `elapsed > 60` and `antibiotics_given == False`:
- `trigger_alarm = True`
- Protocol violation added to `missing_actions`
- Audit trail entry with exact elapsed time appended

### How the Alarm Is Triggered

The **Alert Agent** receives `trigger_alarm = True` and:
1. Sets `alert_banner = "🚨 CRITICAL ALARM: LIFE-THREATENING STATE"`
2. Applies the `alarm-bg pulse-alarm` CSS class (pulsing red animation)
3. Sets `key_message = "CRITICAL INTERVENTION REQUIRED. Follow SEP-1 Bundle."`

The UI refreshes every ~0.4 seconds via Streamlit's live loop, making the alarm immediately visible.

---

## 📖 Example Scenario

**Patient: ICU-ALPHA-92 | Scenario: Septic Shock**

| Time | Event |
|---|---|
| T+0 min | Patient admitted. HR=95, SBP=112, Lactate=1.5. Monitoring begins. |
| T+15 min | Vitals begin deteriorating per scenario physics. |
| **T+19 min** | **Detection Agent fires**: HR=101, SBP=94, Lactate=2.3 → `deterioration_start_time = "19:13"` |
| T+20 min | Clinical Override Agent: Lactate 2.3 → sets risk to HIGH |
| T+20–79 min | Compliance Agent: Countdown active. "Administer antibiotics within 40 mins (SEP-1 window)." |
| **T+79 min** | **60-minute window exceeded. No antibiotics administered.** |
| T+79 min | `trigger_alarm = True` → Compliance violation logged |
| T+79 min | Alert Agent fires: Red pulsing banner → `"🚨 CRITICAL ALARM: LIFE-THREATENING STATE"` |
| T+79 min | Reasoning Agent: Groq LLaMA-3 generates clinical narrative explaining the violation |
| T+79 min | Audit Trail: `"19:13 → deterioration detected"` + `"20:13 → antibiotics delay (66 mins)"` |

> **System verdict**: **CRITICAL PROTOCOL VIOLATION — SEP-1 Bundle Breached. Immediate escalation required.**

---

## 🛠️ Technologies Used

### Frontend

| Tool | Purpose |
|---|---|
| **Streamlit** | Real-time ICU dashboard with live charts, glass-morphism UI |
| **Custom CSS** | Orbitron + Inter fonts, pulsing alarm animations, glassmorphism panels |
| **Pandas** | In-session vital history for trend charts |

### Backend

| Tool | Purpose |
|---|---|
| **FastAPI** | REST API exposing `/predict` endpoint for external consumption |
| **Uvicorn** | ASGI server for the FastAPI backend |
| **Python 3.10+** | Core runtime |
| **joblib** | XGBoost model serialization/loading |

### AI / ML

| Tool | Purpose |
|---|---|
| **XGBoost** | Pre-trained sepsis risk prediction model (`sepsis_model.pkl`) |
| **Groq API (LLaMA-3 8B)** | Live LLM reasoning for human-readable alarm explanations |
| **Shock Index Feature** | Derived feature (HR/SBP) computed at inference time |

### Multi-Agent Framework

| Tool | Purpose |
|---|---|
| **LangGraph** | Directed acyclic graph (DAG) pipeline orchestration for 7 agents |
| **LangChain** | Foundation for agent communication and state management |
| **TypedDict (PatientState)** | Strongly-typed shared state passed between all agents |

### Data Handling

| Tool | Purpose |
|---|---|
| **JSON Patient Timeline** | Simulated EMR data stream with configurable deterioration scenarios |
| **Simulation Physics** | 4 configurable scenarios: Acute Onset, Septic Shock, Slow Drift, Extreme Failure |
| **Pydantic Schemas** | Input validation for FastAPI endpoint (`schema.py`) |

### Alerting

| Tool | Purpose |
|---|---|
| **CSS Pulse Animation** | Pulsing red critical banner on protocol breach |
| **Streamlit Toasts** | Instant feedback on doctor action button clicks |
| **Audit Trail Log** | Monospaced clinical event log rendered in expander panel |

---

## 📁 Folder Structure

```
guardian-ai-sepsis/
│
├── app.py                    # (alias: ui.py) Streamlit dashboard entry point
├── ui.py                     # Full premium ICU monitoring UI
├── main.py                   # FastAPI REST API server
│
├── multi_agent_system.py     # 🧠 Core: LangGraph pipeline with all 7 agents
│
├── model.py                  # XGBoost model loader, feature prep, prediction
├── sepsis_model.pkl          # Pre-trained XGBoost binary
│
├── rules.py                  # Clinical alert rules (SIRS / Sepsis-3 thresholds)
├── logic.py                  # Hybrid decision logic (ML + clinical rules)
├── schema.py                 # Pydantic input/output schemas for FastAPI
│
├── icu_simulation.py         # ICU patient data simulation engine
├── test_pipeline.py          # Integration test for full agent pipeline
├── test_api.py               # FastAPI endpoint smoke test
├── test_st.py                # Streamlit smoke test
│
├── run.bat                   # Windows launcher: starts FastAPI + Streamlit
├── run_agents.bat            # Windows launcher: standalone agent pipeline
│
└── README.md                 # This file
```

---

## 🚀 Getting Started

### Prerequisites

```bash
pip install streamlit fastapi uvicorn langgraph langchain xgboost joblib pandas requests pydantic
```

### Running the Full System

**Option 1 — Windows (Recommended):**
```bat
run.bat
```
This starts the FastAPI backend on `http://localhost:8000` and the Streamlit dashboard simultaneously.

**Option 2 — Manual:**
```bash
# Terminal 1: Start the API
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start the UI
streamlit run ui.py
```

### Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `GROQ_API_KEY` | Groq API key for LLaMA-3 reasoning | Hard-coded fallback |

### Using the Dashboard

1. Open `http://localhost:8501` in your browser
2. Set **Patient ID** and initial vitals in the sidebar
3. Select a **Simulation Scenario** (e.g., "Septic Shock")
4. Click **SET BASELINE & START MONITORING**
5. Watch the system autonomously detect deterioration and start the compliance timer
6. When prompted, click **💉 Administer Antibiotics** to satisfy the SEP-1 protocol — or wait 60 minutes to trigger a CRITICAL alarm

---

## 🔬 What Makes This Unique

Most clinical AI tools stop at prediction. Guardian AI goes further:

```
Traditional System:  Deterioration → Alert → ??? (Waiting for humans)
                                               ↑
                                         THE SILENT GAP

Guardian AI:         Deterioration → Alert → Timer starts → Checks for action
                                                              → No action? ESCALATE
```

The system treats **clinician inaction** as a measurable, detectable clinical event — and responds to it as vigorously as it responds to any worsening vital sign.

---

## 🗺️ Future Improvements

| Feature | Description |
|---|---|
| 🏥 **Real EMR Integration** | Connect to FHIR/HL7 feeds from Epic, Cerner, or OpenEMR |
| 📱 **SMS / WhatsApp Alerts** | Notify on-call doctors via Twilio when escalation fires |
| 📧 **Email Escalation Chain** | Auto-email charge nurse → attending → ICU director on timeout |
| 🖥️ **Central ICU Dashboard** | Multi-bed overview — all patients in a single view |
| 🧪 **More Disease Protocols** | Extend beyond sepsis to ARDS, AKI, stroke, PE bundles |
| 🔒 **HIPAA-Compliant Logging** | Encrypted audit trails with role-based access control |
| 📊 **Shift Report Generation** | LLM-generated end-of-shift summary of all alerts and responses |
| 🤝 **EHR Write-Back** | Automatically document alerts and interventions in patient chart |

---

## 👥 Team

ChainOfThought

Built for **ET GenAI Hackathon** — demonstrating that AI in healthcare must go beyond prediction toward **accountability**.

---
---

<div align="center">

**"Detecting deterioration is necessary. Detecting inaction is what saves lives."**

*Guardian AI — Because a missed alert is not the problem. A missed intervention is.*

</div>
