"""
ML Model Training Script for Disease Risk Prediction
Trains robust Scikit-Learn Random Forest classifiers for:
1. Diabetes Risk Prediction (Pima Indians Diabetes Feature Specification)
2. Cardiovascular Heart Disease Risk Prediction (UCI Heart Disease Feature Specification)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / 'ml_models'
DATA_DIR = BASE_DIR / 'data'
MODEL_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def generate_diabetes_dataset(n_samples=1200, random_state=42):
    """
    Generates realistic clinical distribution aligned with the Pima Indian Diabetes dataset.
    Features:
    - Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
    """
    np.random.seed(random_state)
    
    # Healthy vs Diabetic distributions
    n_diabetic = int(n_samples * 0.40)
    n_healthy = n_samples - n_diabetic
    
    # Healthy cluster
    h_pregnancies = np.random.poisson(lam=2.5, size=n_healthy).clip(0, 14)
    h_glucose = np.random.normal(loc=102, scale=18, size=n_healthy).clip(65, 145)
    h_bp = np.random.normal(loc=70, scale=10, size=n_healthy).clip(55, 95)
    h_skin = np.random.normal(loc=20, scale=8, size=n_healthy).clip(8, 45)
    h_insulin = np.random.normal(loc=85, scale=35, size=n_healthy).clip(20, 220)
    h_bmi = np.random.normal(loc=26.5, scale=4.5, size=n_healthy).clip(18.5, 38.0)
    h_dpf = np.random.gamma(shape=2.0, scale=0.18, size=n_healthy).clip(0.08, 1.2)
    h_age = np.random.normal(loc=31, scale=9, size=n_healthy).clip(21, 75).astype(int)
    h_target = np.zeros(n_healthy, dtype=int)
    
    # Diabetic / High-Risk cluster
    d_pregnancies = np.random.poisson(lam=4.8, size=n_diabetic).clip(0, 17)
    d_glucose = np.random.normal(loc=152, scale=28, size=n_diabetic).clip(110, 230)
    d_bp = np.random.normal(loc=82, scale=12, size=n_diabetic).clip(65, 120)
    d_skin = np.random.normal(loc=31, scale=10, size=n_diabetic).clip(12, 60)
    d_insulin = np.random.normal(loc=185, scale=80, size=n_diabetic).clip(40, 480)
    d_bmi = np.random.normal(loc=35.8, scale=6.5, size=n_diabetic).clip(24.0, 55.0)
    d_dpf = np.random.gamma(shape=3.2, scale=0.25, size=n_diabetic).clip(0.15, 2.4)
    d_age = np.random.normal(loc=46, scale=12, size=n_diabetic).clip(24, 82).astype(int)
    d_target = np.ones(n_diabetic, dtype=int)
    
    df_healthy = pd.DataFrame({
        'pregnancies': h_pregnancies,
        'glucose': np.round(h_glucose, 1),
        'blood_pressure': np.round(h_bp, 1),
        'skin_thickness': np.round(h_skin, 1),
        'insulin': np.round(h_insulin, 1),
        'bmi': np.round(h_bmi, 1),
        'diabetes_pedigree': np.round(h_dpf, 3),
        'age': h_age,
        'outcome': h_target
    })
    
    df_diabetic = pd.DataFrame({
        'pregnancies': d_pregnancies,
        'glucose': np.round(d_glucose, 1),
        'blood_pressure': np.round(d_bp, 1),
        'skin_thickness': np.round(d_skin, 1),
        'insulin': np.round(d_insulin, 1),
        'bmi': np.round(d_bmi, 1),
        'diabetes_pedigree': np.round(d_dpf, 3),
        'age': d_age,
        'outcome': d_target
    })
    
    df = pd.concat([df_healthy, df_diabetic], ignore_index=True).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    df.to_csv(DATA_DIR / 'diabetes_dataset.csv', index=False)
    return df


def generate_heart_disease_dataset(n_samples=1200, random_state=42):
    """
    Generates realistic clinical distribution aligned with the UCI Cleveland Heart Disease dataset.
    Features:
    - age, sex, cp (chest pain), trestbps (resting bp), chol (cholesterol), fbs (fasting sugar),
      restecg (resting ecg), thalach (max HR), exang (angina), oldpeak (ST depression),
      slope, ca (vessels), thal
    """
    np.random.seed(random_state)
    n_positive = int(n_samples * 0.46)
    n_negative = n_samples - n_positive
    
    # Healthy / Low-Risk cluster
    h_age = np.random.normal(loc=49, scale=9, size=n_negative).clip(28, 75).astype(int)
    h_sex = np.random.choice([0, 1], size=n_negative, p=[0.45, 0.55])
    h_cp = np.random.choice([0, 1, 2, 3], size=n_negative, p=[0.55, 0.20, 0.18, 0.07])
    h_trestbps = np.random.normal(loc=122, scale=14, size=n_negative).clip(90, 160).astype(int)
    h_chol = np.random.normal(loc=225, scale=35, size=n_negative).clip(130, 310).astype(int)
    h_fbs = np.random.choice([0, 1], size=n_negative, p=[0.88, 0.12])
    h_restecg = np.random.choice([0, 1, 2], size=n_negative, p=[0.60, 0.38, 0.02])
    h_thalach = np.random.normal(loc=162, scale=18, size=n_negative).clip(115, 205).astype(int)
    h_exang = np.random.choice([0, 1], size=n_negative, p=[0.86, 0.14])
    h_oldpeak = np.random.exponential(scale=0.45, size=n_negative).clip(0.0, 2.5)
    h_slope = np.random.choice([0, 1, 2], size=n_negative, p=[0.10, 0.65, 0.25])
    h_ca = np.random.choice([0, 1, 2, 3], size=n_negative, p=[0.82, 0.12, 0.05, 0.01])
    h_thal = np.random.choice([1, 2, 3], size=n_negative, p=[0.20, 0.72, 0.08])
    h_target = np.zeros(n_negative, dtype=int)
    
    # High-Risk / Heart Disease cluster
    d_age = np.random.normal(loc=58, scale=8, size=n_positive).clip(35, 82).astype(int)
    d_sex = np.random.choice([0, 1], size=n_positive, p=[0.25, 0.75])
    d_cp = np.random.choice([0, 1, 2, 3], size=n_positive, p=[0.15, 0.18, 0.22, 0.45])
    d_trestbps = np.random.normal(loc=142, scale=18, size=n_positive).clip(105, 200).astype(int)
    d_chol = np.random.normal(loc=272, scale=48, size=n_positive).clip(170, 480).astype(int)
    d_fbs = np.random.choice([0, 1], size=n_positive, p=[0.75, 0.25])
    d_restecg = np.random.choice([0, 1, 2], size=n_positive, p=[0.35, 0.58, 0.07])
    d_thalach = np.random.normal(loc=134, scale=22, size=n_positive).clip(75, 175).astype(int)
    d_exang = np.random.choice([0, 1], size=n_positive, p=[0.38, 0.62])
    d_oldpeak = np.random.normal(loc=1.8, scale=1.1, size=n_positive).clip(0.0, 5.5)
    d_slope = np.random.choice([0, 1, 2], size=n_positive, p=[0.25, 0.35, 0.40])
    d_ca = np.random.choice([0, 1, 2, 3], size=n_positive, p=[0.28, 0.40, 0.22, 0.10])
    d_thal = np.random.choice([1, 2, 3], size=n_positive, p=[0.05, 0.30, 0.65])
    d_target = np.ones(n_positive, dtype=int)
    
    df_healthy = pd.DataFrame({
        'age': h_age, 'sex': h_sex, 'cp': h_cp, 'trestbps': h_trestbps, 'chol': h_chol,
        'fbs': h_fbs, 'restecg': h_restecg, 'thalach': h_thalach, 'exang': h_exang,
        'oldpeak': np.round(h_oldpeak, 2), 'slope': h_slope, 'ca': h_ca, 'thal': h_thal,
        'target': h_target
    })
    
    df_disease = pd.DataFrame({
        'age': d_age, 'sex': d_sex, 'cp': d_cp, 'trestbps': d_trestbps, 'chol': d_chol,
        'fbs': d_fbs, 'restecg': d_restecg, 'thalach': d_thalach, 'exang': d_exang,
        'oldpeak': np.round(d_oldpeak, 2), 'slope': d_slope, 'ca': d_ca, 'thal': d_thal,
        'target': d_target
    })
    
    df = pd.concat([df_healthy, df_disease], ignore_index=True).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    df.to_csv(DATA_DIR / 'heart_disease_dataset.csv', index=False)
    return df


def train_models():
    print("=" * 60)
    print("Starting Training for Healthcare Disease Prediction Models")
    print("=" * 60)
    
    # ---------------- 1. DIABETES MODEL ----------------
    print("\n[1/2] Training Diabetes Risk Prediction Model...")
    df_diabetes = generate_diabetes_dataset()
    diabetes_features = [
        'pregnancies', 'glucose', 'blood_pressure', 'skin_thickness',
        'insulin', 'bmi', 'diabetes_pedigree', 'age'
    ]
    X_diab = df_diabetes[diabetes_features]
    y_diab = df_diabetes['outcome']
    
    X_d_train, X_d_test, y_d_train, y_d_test = train_test_split(
        X_diab, y_diab, test_size=0.2, random_state=42, stratify=y_diab
    )
    
    diabetes_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(
            n_estimators=150,
            max_depth=7,
            min_samples_split=4,
            random_state=42,
            class_weight='balanced'
        ))
    ])
    
    diabetes_pipeline.fit(X_d_train, y_d_train)
    y_d_pred = diabetes_pipeline.predict(X_d_test)
    y_d_prob = diabetes_pipeline.predict_proba(X_d_test)[:, 1]
    
    d_acc = accuracy_score(y_d_test, y_d_pred)
    d_prec = precision_score(y_d_test, y_d_pred)
    d_rec = recall_score(y_d_test, y_d_pred)
    d_f1 = f1_score(y_d_test, y_d_pred)
    d_auc = roc_auc_score(y_d_test, y_d_prob)
    
    print(f"  Diabetes Model Accuracy:  {d_acc * 100:.2f}%")
    print(f"  Diabetes Model Precision: {d_prec * 100:.2f}%")
    print(f"  Diabetes Model Recall:    {d_rec * 100:.2f}%")
    print(f"  Diabetes Model F1-Score:  {d_f1:.4f}")
    print(f"  Diabetes Model ROC-AUC:   {d_auc:.4f}")
    
    # Save Diabetes Pipeline
    diabetes_model_path = MODEL_DIR / 'diabetes_model.joblib'
    joblib.dump({
        'pipeline': diabetes_pipeline,
        'features': diabetes_features,
        'metrics': {
            'accuracy': round(d_acc * 100, 2),
            'precision': round(d_prec * 100, 2),
            'recall': round(d_rec * 100, 2),
            'f1_score': round(d_f1, 4),
            'roc_auc': round(d_auc, 4)
        }
    }, diabetes_model_path)
    print(f"  --> Saved to {diabetes_model_path}")
    
    # ---------------- 2. HEART DISEASE MODEL ----------------
    print("\n[2/2] Training Heart Disease Risk Prediction Model...")
    df_heart = generate_heart_disease_dataset()
    heart_features = [
        'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs',
        'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
    ]
    X_heart = df_heart[heart_features]
    y_heart = df_heart['target']
    
    X_h_train, X_h_test, y_h_train, y_h_test = train_test_split(
        X_heart, y_heart, test_size=0.2, random_state=42, stratify=y_heart
    )
    
    heart_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(
            n_estimators=150,
            max_depth=7,
            min_samples_split=4,
            random_state=42,
            class_weight='balanced'
        ))
    ])
    
    heart_pipeline.fit(X_h_train, y_h_train)
    y_h_pred = heart_pipeline.predict(X_h_test)
    y_h_prob = heart_pipeline.predict_proba(X_h_test)[:, 1]
    
    h_acc = accuracy_score(y_h_test, y_h_pred)
    h_prec = precision_score(y_h_test, y_h_pred)
    h_rec = recall_score(y_h_test, y_h_pred)
    h_f1 = f1_score(y_h_test, y_h_pred)
    h_auc = roc_auc_score(y_h_test, y_h_prob)
    
    print(f"  Heart Disease Accuracy:   {h_acc * 100:.2f}%")
    print(f"  Heart Disease Precision:  {h_prec * 100:.2f}%")
    print(f"  Heart Disease Recall:     {h_rec * 100:.2f}%")
    print(f"  Heart Disease F1-Score:   {h_f1:.4f}")
    print(f"  Heart Disease ROC-AUC:    {h_auc:.4f}")
    
    # Save Heart Disease Pipeline
    heart_model_path = MODEL_DIR / 'heart_disease_model.joblib'
    joblib.dump({
        'pipeline': heart_pipeline,
        'features': heart_features,
        'metrics': {
            'accuracy': round(h_acc * 100, 2),
            'precision': round(h_prec * 100, 2),
            'recall': round(h_rec * 100, 2),
            'f1_score': round(h_f1, 4),
            'roc_auc': round(h_auc, 4)
        }
    }, heart_model_path)
    print(f"  --> Saved to {heart_model_path}")
    
    # Save combined metadata
    meta = {
        'diabetes': {
            'features': diabetes_features,
            'accuracy': round(d_acc * 100, 2),
            'roc_auc': round(d_auc, 4),
        },
        'heart_disease': {
            'features': heart_features,
            'accuracy': round(h_acc * 100, 2),
            'roc_auc': round(h_auc, 4),
        }
    }
    with open(MODEL_DIR / 'metadata.json', 'w') as f:
        json.dump(meta, f, indent=2)
        
    print("\nBoth models successfully trained and serialized!")
    print("=" * 60)


if __name__ == '__main__':
    train_models()

