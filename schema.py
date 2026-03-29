from pydantic import BaseModel
from typing import List, Optional

class PatientData(BaseModel):
    HR: float
    O2Sat: float
    Temp: float
    SBP: float
    MAP: float
    Resp: float
    Lactate: float
    WBC: float
    Platelets: float
    Creatinine: float

class PredictionResponse(BaseModel):
    risk: float
    alerts: List[str]
    missing_actions: List[str]
    decision: str
    explanation: str
