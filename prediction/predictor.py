import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / 'ml_models'

_DIABETES_DATA = None
_HEART_DATA = None


def get_diabetes_model():
    global _DIABETES_DATA
    if _DIABETES_DATA is None:
        model_path = MODEL_DIR / 'diabetes_model.joblib'
        if not model_path.exists():
            from .train_models import train_models
            train_models()
        _DIABETES_DATA = joblib.load(model_path)
    return _DIABETES_DATA


def get_heart_disease_model():
    global _HEART_DATA
    if _HEART_DATA is None:
        model_path = MODEL_DIR / 'heart_disease_model.joblib'
        if not model_path.exists():
            from .train_models import train_models
            train_models()
        _HEART_DATA = joblib.load(model_path)
    return _HEART_DATA


def predict_diabetes_risk(data):
    """
    Predict diabetes risk given user input data.
    Expected keys:
    - pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree, age
    """
    model_obj = get_diabetes_model()
    pipeline = model_obj['pipeline']
    features = model_obj['features']
    
    # Clean and order input features
    row = []
    for f in features:
        val = float(data.get(f, 0))
        row.append(val)
        
    df_input = pd.DataFrame([row], columns=features)
    prob = float(pipeline.predict_proba(df_input)[0, 1])
    score = round(prob * 100.0, 1)
    
    # Classify Risk Level
    if score >= 65.0:
        level = 'HIGH'
    elif score >= 35.0:
        level = 'MODERATE'
    else:
        level = 'LOW'
        
    label = 1 if prob >= 0.5 else 0
    
    # Clinical factors breakdown
    factors = []
    glucose = float(data.get('glucose', 0))
    bmi = float(data.get('bmi', 0))
    bp = float(data.get('blood_pressure', 0))
    insulin = float(data.get('insulin', 0))
    pedigree = float(data.get('diabetes_pedigree', 0))
    age = float(data.get('age', 0))
    
    if glucose >= 140:
        factors.append(f"Elevated Plasma Glucose: {glucose} mg/dL (Normal fasting is 70-100 mg/dL).")
    elif glucose >= 115:
        factors.append(f"Borderline Fasting Glucose: {glucose} mg/dL (Pre-diabetes risk).")
        
    if bmi >= 30:
        factors.append(f"High Body Mass Index (BMI): {bmi:.1f} kg/m² (Clinical obesity).")
    elif bmi >= 25:
        factors.append(f"Overweight BMI: {bmi:.1f} kg/m².")
        
    if bp >= 90:
        factors.append(f"Elevated Diastolic Blood Pressure: {bp} mm Hg (Hypertension stage 2).")
    elif bp >= 80:
        factors.append(f"Pre-hypertensive Blood Pressure: {bp} mm Hg.")
        
    if insulin >= 160:
        factors.append(f"High Serum Insulin Level: {insulin} µU/mL (Insulin resistance indicator).")
        
    if pedigree >= 0.6:
        factors.append(f"Elevated Diabetes Pedigree Score: {pedigree:.2f} (Family history risk factor).")
        
    if age >= 45:
        factors.append(f"Age Risk Factor: {int(age)} years (Risk naturally elevates past 45).")
        
    # Recommendations
    recs = []
    if level == 'HIGH':
        recs.append("Urgent Consultation: Book an appointment with an Endocrinologist or Diabetologist for an HbA1c test.")
        recs.append("Dietary Adjustment: Eliminate refined carbohydrates, sweetened beverages, and saturated fats.")
        recs.append("Vitals Tracking: Monitor fasting and 2-hour postprandial glucose levels weekly.")
    elif level == 'MODERATE':
        recs.append("Medical Review: Schedule a routine checkup and complete fasting blood sugar profile.")
        recs.append("Lifestyle Management: Adopt moderate aerobic exercise (30 minutes daily, 5 days/week).")
        recs.append("Weight Management: Aim for a 5-7% weight reduction to significantly lower metabolic risks.")
    else:
        recs.append("Maintain Healthy Routine: Balanced Mediterranean/high-fiber diet with low processed sugar.")
        recs.append("Annual Screening: Re-evaluate blood glucose annually during your periodic physical.")
        
    return {
        'risk_score': score,
        'risk_level': level,
        'prediction_label': label,
        'contributing_factors': factors,
        'recommendations': " \n".join(recs),
        'recommended_specialty': 'Endocrinology',
    }


def predict_heart_disease_risk(data):
    """
    Predict cardiovascular heart disease risk given user input data.
    Expected keys:
    - age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
    """
    model_obj = get_heart_disease_model()
    pipeline = model_obj['pipeline']
    features = model_obj['features']
    
    row = []
    for f in features:
        val = float(data.get(f, 0))
        row.append(val)
        
    df_input = pd.DataFrame([row], columns=features)
    prob = float(pipeline.predict_proba(df_input)[0, 1])
    score = round(prob * 100.0, 1)
    
    if score >= 65.0:
        level = 'HIGH'
    elif score >= 35.0:
        level = 'MODERATE'
    else:
        level = 'LOW'
        
    label = 1 if prob >= 0.5 else 0
    
    factors = []
    trestbps = float(data.get('trestbps', 0))
    chol = float(data.get('chol', 0))
    thalach = float(data.get('thalach', 0))
    oldpeak = float(data.get('oldpeak', 0))
    cp = int(data.get('cp', 0))
    exang = int(data.get('exang', 0))
    ca = int(data.get('ca', 0))
    
    if trestbps >= 140:
        factors.append(f"High Resting Blood Pressure: {trestbps} mm Hg (Stage 2 Hypertension).")
    elif trestbps >= 130:
        factors.append(f"Pre-hypertensive Resting Blood Pressure: {trestbps} mm Hg.")
        
    if chol >= 240:
        factors.append(f"High Serum Cholesterol: {chol} mg/dL (Hypercholesterolemia).")
    elif chol >= 200:
        factors.append(f"Borderline High Cholesterol: {chol} mg/dL.")
        
    if oldpeak >= 1.5:
        factors.append(f"Significant ST Depression: {oldpeak:.1f} mm during exercise (Indicates myocardial ischemia).")
        
    if cp in [1, 2, 3]:
        factors.append("Reported Chest Pain / Anginal Discomfort under stress.")
        
    if exang == 1:
        factors.append("Exercise-Induced Angina present during physical exertion.")
        
    if thalach < 120 and thalach > 0:
        factors.append(f"Subnormal Maximum Heart Rate response: {int(thalach)} bpm.")
        
    if ca > 0:
        factors.append(f"Fluoroscopy detected {ca} major vessels with calcification/blockage.")
        
    recs = []
    if level == 'HIGH':
        recs.append("Immediate Evaluation: Book a priority consultation with a Cardiologist for an Echo / TMT stress test.")
        recs.append("Symptom Monitoring: Seek immediate emergency care if experiencing crushing chest pressure, shortness of breath, or radiating arm pain.")
        recs.append("Cardiovascular Diet: Strict sodium restriction (<1,500 mg/day) and low saturated fat intake.")
    elif level == 'MODERATE':
        recs.append("Cardiology Screening: Schedule an ECG, Lipid profile, and Blood Pressure 24-hr holter monitoring.")
        recs.append("Lifestyle Intervention: Begin doctor-approved moderate cardiovascular exercise.")
        recs.append("Stress Management: Engage in mindfulness, adequate sleep, and tobacco/alcohol cessation.")
    else:
        recs.append("Heart-Healthy Diet: Continue balanced nutrient-rich diet rich in omega-3 fatty acids, vegetables, and whole grains.")
        recs.append("Regular Activity: Maintain at least 150 minutes of moderate aerobic physical activity per week.")
        recs.append("Periodic Checkups: Monitor blood pressure and lipid profile every 12 to 24 months.")
        
    return {
        'risk_score': score,
        'risk_level': level,
        'prediction_label': label,
        'contributing_factors': factors,
        'recommendations': " \n".join(recs),
        'recommended_specialty': 'Cardiology',
    }
