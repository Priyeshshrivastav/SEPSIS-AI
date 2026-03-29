from fastapi import FastAPI, HTTPException
from schema import PatientData, PredictionResponse
from model import load_model, prepare_input, predict_risk
from rules import evaluate_clinical_rules, add_critical_actions
from logic import get_decision, generate_explanation
import uvicorn
import os

app = FastAPI(title="Sepsis Detection AI Agent System (Hackathon Polished)")

# Load model globally (once upon start)
model = None
try:
    model = load_model()
except Exception as e:
    print(f"FAILED TO LOAD XGBOOST MODEL: {e}")

@app.get("/")
def read_root():
    return {"status": "active", "description": "Sepsis AI Detection Engine is live."}

@app.post("/predict", response_model=PredictionResponse)
def predict(data: PatientData):
    """Predict risk, identify clinical alerts and suggest actions."""
    if model is None:
        raise HTTPException(status_code=500, detail="Sepsis model not loaded on server side.")
        
    patient_dict = data.dict()
    
    # 1. Feature Pre-processing (STRICT ORDER)
    processed_input = prepare_input(patient_dict)
    
    # 2. Machine Learning Prediction (AI Score)
    risk = predict_risk(model, processed_input)
    
    # 3. Clinical Alerts Detection (Rule Engine)
    alerts, current_actions = evaluate_clinical_rules(patient_dict)
    
    # 4. HYBRID Decision Logic (AI + RULES)
    decision = get_decision(patient_dict, risk, alerts)
    
    # 5. Enrichment: Add critical missing actions based on decision and risk
    final_actions = add_critical_actions(decision, risk, current_actions)
    
    # 6. AI Explainability: Human-readable explanation
    explanation = generate_explanation(risk, alerts, decision)
    
    return PredictionResponse(
        risk=risk,
        alerts=alerts,
        missing_actions=final_actions,
        decision=decision,
        explanation=explanation
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
