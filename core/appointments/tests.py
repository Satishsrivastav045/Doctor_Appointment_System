from datetime import date, time, timedelta

from django.urls import reverse
from django.test import TestCase

from accounts.models import Patient, Role, User
from doctors.models import Availability, Doctor
from .models import Appointment


class AppointmentFlowTests(TestCase):
    def setUp(self):
        self.patient_role = Role.objects.create(role_name="patient")
        self.doctor_role = Role.objects.create(role_name="doctor")

        self.patient_user = User.objects.create_user(
            username="patient_user",
            password="testpass123",
            role=self.patient_role,
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            patient_name="Test Patient",
        )

        self.doctor_user = User.objects.create_user(
            username="doctor_user",
            password="testpass123",
            role=self.doctor_role,
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            name="Dr Test",
            specialization="General Physician",
        )
        self.slot = Availability.objects.create(
            doctor=self.doctor,
            available_date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(10, 30),
        )

    def test_patient_can_book_available_slot(self):
        self.client.login(username="patient_user", password="testpass123")

        response = self.client.post(
            reverse("book_appointment", args=[self.doctor.id]),
            {"slot_id": self.slot.id},
        )

        self.assertRedirects(response, reverse("patient_dashboard"))
        appointment = Appointment.objects.get(patient=self.patient, doctor=self.doctor)
        self.assertEqual(appointment.status, "pending")
        self.slot.refresh_from_db()
        self.assertTrue(self.slot.is_booked)

    def test_doctor_can_update_own_appointment_status(self):
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            availability=self.slot,
            appointment_date=self.slot.available_date,
        )
        self.client.login(username="doctor_user", password="testpass123")

        response = self.client.get(reverse("update_status", args=[appointment.id, "approved"]))

        self.assertRedirects(response, reverse("doctor_dashboard"))
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, "confirmed")

    def test_doctor_user_cannot_book_patient_appointment(self):
        self.client.login(username="doctor_user", password="testpass123")

        response = self.client.post(
            reverse("book_appointment", args=[self.doctor.id]),
            {"slot_id": self.slot.id},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Appointment.objects.exists())
