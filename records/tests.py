from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User, DoctorProfile, PatientProfile
from appointments.models import Appointment
from records.models import MedicalRecord
import datetime


class SecureStorageRBACTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Patients
        self.patient1 = User.objects.create_user(
            username='patient1', email='p1@test.com', password='password123', role=User.Role.PATIENT
        )
        PatientProfile.objects.create(user=self.patient1)

        self.patient2 = User.objects.create_user(
            username='patient2', email='p2@test.com', password='password123', role=User.Role.PATIENT
        )
        PatientProfile.objects.create(user=self.patient2)

        # Doctors
        self.doctor_assigned = User.objects.create_user(
            username='doc_assigned', email='da@test.com', password='password123', role=User.Role.DOCTOR
        )
        DoctorProfile.objects.create(user=self.doctor_assigned, specialty='Cardiology', license_number='LIC-1')

        self.doctor_stranger = User.objects.create_user(
            username='doc_stranger', email='ds@test.com', password='password123', role=User.Role.DOCTOR
        )
        DoctorProfile.objects.create(user=self.doctor_stranger, specialty='Orthopedics', license_number='LIC-2')

        # Admin
        self.admin = User.objects.create_superuser(
            username='admin_user', email='admin@test.com', password='password123', role=User.Role.ADMIN
        )

        # Appointment between patient1 and doctor_assigned
        self.appt = Appointment.objects.create(
            patient=self.patient1,
            doctor=self.doctor_assigned,
            appointment_date=datetime.date.today(),
            appointment_time=datetime.time(10, 0),
            status=Appointment.Status.CONFIRMED,
            symptoms='Chest discomfort'
        )

        # Medical Record uploaded for patient1
        fake_file = SimpleUploadedFile("test_report.pdf", b"Confidential Medical PDF Data", content_type="application/pdf")
        self.record = MedicalRecord.objects.create(
            patient=self.patient1,
            uploaded_by=self.patient1,
            title="Blood Chemistry Panel",
            record_type=MedicalRecord.RecordType.LAB_REPORT,
            record_date=datetime.date.today(),
            file=fake_file
        )

    def test_owner_patient_can_download_record(self):
        self.client.login(username='patient1', password='password123')
        response = self.client.get(reverse('records:download', args=[self.record.id]))
        self.assertEqual(response.status_code, 200)

    def test_stranger_patient_cannot_access_record(self):
        self.client.login(username='patient2', password='password123')
        # Patient 2 tries to download Patient 1's record -> Should be 403 Forbidden
        response = self.client.get(reverse('records:download', args=[self.record.id]))
        self.assertEqual(response.status_code, 403)

    def test_assigned_doctor_can_access_record(self):
        self.client.login(username='doc_assigned', password='password123')
        response = self.client.get(reverse('records:download', args=[self.record.id]))
        self.assertEqual(response.status_code, 200)

    def test_stranger_doctor_cannot_access_record(self):
        self.client.login(username='doc_stranger', password='password123')
        response = self.client.get(reverse('records:download', args=[self.record.id]))
        self.assertEqual(response.status_code, 403)

    def test_hospital_admin_can_access_record(self):
        self.client.login(username='admin_user', password='password123')
        response = self.client.get(reverse('records:download', args=[self.record.id]))
        self.assertEqual(response.status_code, 200)
