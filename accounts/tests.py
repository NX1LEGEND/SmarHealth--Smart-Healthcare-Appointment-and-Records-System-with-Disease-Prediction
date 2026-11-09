from django.test import TestCase, Client
from django.urls import reverse
from .models import User, DoctorProfile, PatientProfile


class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient_user = User.objects.create_user(
            username='patient_test',
            email='patient@test.com',
            password='password123',
            role=User.Role.PATIENT,
            first_name='Test',
            last_name='Patient'
        )
        PatientProfile.objects.create(user=self.patient_user)

        self.doctor_user = User.objects.create_user(
            username='doctor_test',
            email='doctor@test.com',
            password='password123',
            role=User.Role.DOCTOR,
            first_name='Test',
            last_name='Doctor'
        )
        DoctorProfile.objects.create(
            user=self.doctor_user,
            specialty='Cardiology',
            license_number='LIC-12345',
            qualification='MD Cardiology'
        )

    def test_user_roles(self):
        self.assertTrue(self.patient_user.is_patient)
        self.assertFalse(self.patient_user.is_doctor)
        self.assertTrue(self.doctor_user.is_doctor)
        self.assertFalse(self.doctor_user.is_patient)

    def test_login_redirection(self):
        # Patient login redirects to patient dashboard
        response = self.client.post(reverse('accounts:login'), {
            'username': 'patient_test',
            'password': 'password123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Patient Portal')

    def test_doctor_login_redirection(self):
        # Doctor login redirects to doctor dashboard
        response = self.client.post(reverse('accounts:login'), {
            'username': 'doctor_test',
            'password': 'password123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Doctor Clinical Console')
