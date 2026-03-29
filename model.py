import joblib
import pandas as pd
import os
import numpy as np

# Load pre-trained model path
MODEL_PATH = "sepsis_model.pkl"

def load_model():
    """Reads the local pre-trained XGBoost model pickel."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file {MODEL_PATH} not found.")
    return joblib.load(MODEL_PATH)

def prepare_input(data):
    """
    STRICT REQUIREMENT: Feature order MUST match training EXACTLY:
    [HR, O2Sat, Temp, SBP, MAP, Resp, Lactate, WBC, Platelets, Creatinine, Shock_Index]
    """
    try:
        # Step 1: Compute Shock_Index = HR / SBP
        hr = float(data["HR"])
        sbp = float(data["SBP"])
        shock_index = hr / sbp if sbp != 0 else 0.0
        
        # Step 2: Handle feature scaling (WBC/Platelets in thousands as expected by model)
        wbc = float(data["WBC"])
        if wbc > 500: wbc /= 1000.0
        
        platelets = float(data["Platelets"])
        if platelets > 500: platelets /= 1000.0

        # Step 3: Bundle features in EXACT same order as model was trained 
        input_data = [
            hr,
            float(data["O2Sat"]),
            float(data["Temp"]),
            sbp,
            float(data["MAP"]),
            float(data["Resp"]),
            float(data["Lactate"]),
            wbc,
            platelets,
            float(data["Creatinine"]),
            shock_index
        ]
        
        # HACKATHON DEBUG: print("MODEL INPUT:", input_data)
        print("MODEL INPUT:", input_data)
        
        return [input_data]
    except Exception as e:
        print(f"Error in prepare_input function logic: {e}")
        return [[0.0] * 11]

def predict_risk(model, processed_input: list) -> float:
    """Predict sepsis risk score (0-1) using model.predict_proba."""
    try:
        # Use risk probability of class 1 (Sepsis)
        prediction_proba = model.predict_proba(processed_input)
        risk = float(prediction_proba[0][1])
        return risk
    except Exception as e:
        print(f"CRITICAL: Failed to get prediction from model: {e}")
        return 0.1 # Minimal risk fallback
