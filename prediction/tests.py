from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, PatientProfile
from prediction.models import HealthPrediction
from prediction.predictor import predict_diabetes_risk, predict_heart_disease_risk


class PredictionEngineTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = User.objects.create_user(
            username='diab_patient', email='diab@test.com', password='password123', role=User.Role.PATIENT
        )
        PatientProfile.objects.create(user=self.patient)

    def test_diabetes_low_risk(self):
        normal_vitals = {
            'pregnancies': 1,
            'glucose': 85.0,
            'blood_pressure': 68.0,
            'skin_thickness': 18.0,
            'insulin': 50.0,
            'bmi': 21.5,
            'diabetes_pedigree': 0.20,
            'age': 25
        }
        res = predict_diabetes_risk(normal_vitals)
        self.assertEqual(res['risk_level'], 'LOW')
        self.assertLess(res['risk_score'], 35.0)

    def test_diabetes_high_risk(self):
        high_risk_vitals = {
            'pregnancies': 5,
            'glucose': 185.0,
            'blood_pressure': 95.0,
            'skin_thickness': 38.0,
            'insulin': 240.0,
            'bmi': 38.2,
            'diabetes_pedigree': 0.85,
            'age': 55
        }
        res = predict_diabetes_risk(high_risk_vitals)
        self.assertEqual(res['risk_level'], 'HIGH')
        self.assertGreaterEqual(res['risk_score'], 65.0)
        self.assertIn("Elevated Plasma Glucose", " ".join(res['contributing_factors']))

    def test_heart_disease_low_risk(self):
        normal_cardiac = {
            'age': 35,
            'sex': 1,
            'cp': 0,
            'trestbps': 115,
            'chol': 180,
            'fbs': 0,
            'restecg': 0,
            'thalach': 175,
            'exang': 0,
            'oldpeak': 0.1,
            'slope': 1,
            'ca': 0,
            'thal': 2
        }
        res = predict_heart_disease_risk(normal_cardiac)
        self.assertEqual(res['risk_level'], 'LOW')
        self.assertLess(res['risk_score'], 35.0)

    def test_heart_disease_high_risk(self):
        high_risk_cardiac = {
            'age': 65,
            'sex': 1,
            'cp': 3,
            'trestbps': 160,
            'chol': 310,
            'fbs': 1,
            'restecg': 1,
            'thalach': 110,
            'exang': 1,
            'oldpeak': 2.8,
            'slope': 2,
            'ca': 2,
            'thal': 3
        }
        res = predict_heart_disease_risk(high_risk_cardiac)
        self.assertEqual(res['risk_level'], 'HIGH')
        self.assertGreaterEqual(res['risk_score'], 65.0)

    def test_diabetes_web_submission(self):
        self.client.login(username='diab_patient', password='password123')
        response = self.client.post(reverse('prediction:diabetes'), {
            'pregnancies': 2,
            'glucose': 160.0,
            'blood_pressure': 85.0,
            'skin_thickness': 25.0,
            'insulin': 170.0,
            'bmi': 31.0,
            'diabetes_pedigree': 0.60,
            'age': 48
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(HealthPrediction.objects.filter(patient=self.patient, disease_type=HealthPrediction.Disease.DIABETES).exists())
