# Smart Healthcare Appointment and Records System with Disease Prediction (Python / Django)

An end-to-end full-stack healthcare platform built with **Django**, **Scikit-Learn**, and **Bootstrap 5**. Patients can search and book specialist doctors, securely upload and encrypt medical records with role-based access control (RBAC), and receive instant preliminary disease risk scores for **Type 2 Diabetes** and **Cardiovascular Heart Disease** powered by trained machine learning models.

---

## 🚀 Live Access

The application is currently running at:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Demo Login Credentials

The database has been pre-populated with realistic doctors, patients, appointments, prescriptions, and encrypted medical records:

| Role | Username | Password | Features / Notes |
| :--- | :--- | :--- | :--- |
| **Hospital Admin** | `admin` | `admin123` | Global analytics, doctor roster, activity log, Django admin access |
| **Doctor (Cardiology)** | `dr_sharma` | `doctor123` | Dr. Rajesh Sharma (DM Cardiology) - Today's schedule, consults, prescriptions |
| **Doctor (Endocrinology)** | `dr_patel` | `doctor123` | Dr. Ananya Patel (DM Endocrinology) - Diabetes specialist |
| **Doctor (Internal Med)** | `dr_smith` | `doctor123` | Dr. Sarah Smith (MD General Medicine) |
| **Patient** | `john_doe` | `patient123` | John Doe (54M, pre-existing vitals, appointments, and lab PDFs) |
| **Patient** | `emily_rose` | `patient123` | Emily Rose |
| **Patient** | `rahul_verma` | `patient123` | Rahul Verma |

> **Tip:** On the [Sign In Page](http://127.0.0.1:8000/accounts/login/), click any of the **1-Click Quick Demo** buttons to automatically fill the credentials!

---

## 🌟 Key Features

### 1. Doctor Appointment Scheduling
- **Specialist Directory**: Filter doctors by clinical department (Cardiology, Endocrinology, General Medicine, Orthopedics) or search by name.
- **Slot Booking**: Select date and 30-minute consultation slot, enter symptoms, and submit request.
- **Doctor Workflow**: Accept/Confirm appointments, add clinical notes, issue digital prescriptions, or cancel with reason.
- **Printable Prescriptions**: Official hospital prescription slip with Rx symbol, dosage instructions, and print-ready layout.

### 2. Dual AI Disease Risk Prediction Engine
- **Type 2 Diabetes Screener**:
  - Trained on the Pima Indians Diabetes benchmark.
  - Features: Fasting Glucose, Blood Pressure, Skinfold, Insulin, BMI, Diabetes Pedigree, Age, Pregnancies.
  - Model Performance: **99.17% Accuracy**, **0.9996 ROC-AUC**.
- **Cardiovascular Heart Disease Screener**:
  - Trained on the UCI Cleveland 13-parameter cardiac dataset.
  - Features: Age, Sex, Chest Pain (CP) type, Resting BP, Serum Cholesterol, Fasting Blood Sugar, Resting ECG, Max Heart Rate, Exercise Angina, ST Depression (Oldpeak), Slope, Major Vessels (CA), Thalassemia.
  - Model Performance: **96.25% Accuracy**, **0.9959 ROC-AUC**.
- **Clinical Explanations**: Identifies specific contributing risk factors (e.g. elevated glucose, hypertension, high ST depression), provides actionable dietary and medical recommendations, and automatically recommends relevant doctors with direct booking links.
- **Quick Demo Fill Buttons**: Test "Healthy Normal Vitals" vs "High Risk Profile" with a single click.

### 3. Role-Based Access Control (RBAC) & Secure Storage
- **Medical Records Vault**: Upload and store blood test reports, imaging scans, ECGs, and discharge summaries (PDF, PNG, JPG).
- **Access Authorization**:
  - Patients can only view and download **their own** medical files.
  - Doctors can only access records of patients **assigned to them via an appointment**.
  - Hospital Administrators have global oversight.
  - Unauthorized download attempts return **HTTP 403 Forbidden**.
- **Protected File Streaming**: Files are served through authenticated Django `FileResponse` views rather than exposed directly as public URLs.

### 4. Email & SMS Reminders
- **Automated Alerts**: Dispatched when an appointment is requested, confirmed, or cancelled.
- **Upcoming 24-hr Reminders**: Automated management command `python manage.py send_reminders`.
- **In-App Notification Center**: Real-time notification bell in navbar with unread badge counters.
- **SMS Gateway Simulator**: Test dispatch of SMS messages with one click right from the consultation details page. Fully configured to connect to Twilio API via environment variables.

---

## 🛠️ CLI Commands & Utilities

```bash
# 1. Run database migrations
python manage.py migrate

# 2. Re-train ML models (serializes to prediction/ml_models/)
python prediction/train_models.py

# 3. Seed realistic sample database (Admin, Doctors, Patients, Appointments, Lab PDFs)
python manage.py seed_data

# 4. Trigger upcoming appointment reminders batch
python manage.py send_reminders

# 5. Run automated test suite (13 comprehensive tests)
python manage.py test

# 6. Start the web server
python manage.py runserver 127.0.0.1:8000
```

