from datetime import date, time, timedelta

from django.test import TestCase
from django.urls import reverse

from accounts.models import Role, User
from doctors.models import Availability, Doctor


class AvailabilitySecurityTests(TestCase):
    def setUp(self):
        self.doctor_role = Role.objects.create(role_name="doctor")
        self.patient_role = Role.objects.create(role_name="patient")
        self.doctor_user = User.objects.create_user(
            username="doctor_user",
            password="testpass123",
            role=self.doctor_role,
        )
        self.patient_user = User.objects.create_user(
            username="patient_user",
            password="testpass123",
            role=self.patient_role,
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            name="Dr Secure",
            is_verified=True,
        )
        self.slot = Availability.objects.create(
            doctor=self.doctor,
            available_date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(10, 30),
        )

    def test_delete_availability_requires_post(self):
        self.client.login(username="doctor_user", password="testpass123")

        response = self.client.get(reverse("delete_availability", args=[self.slot.id]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Availability.objects.filter(id=self.slot.id).exists())

    def test_patient_cannot_delete_doctor_availability(self):
        self.client.login(username="patient_user", password="testpass123")

        response = self.client.post(reverse("delete_availability", args=[self.slot.id]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Availability.objects.filter(id=self.slot.id).exists())

    def test_doctor_cannot_add_past_availability(self):
        self.client.login(username="doctor_user", password="testpass123")

        response = self.client.post(
            reverse("manage_availability"),
            {
                "available_date": date.today() - timedelta(days=1),
                "start_time": "09:00",
                "end_time": "09:30",
            },
        )

        self.assertRedirects(response, reverse("manage_availability"))
        self.assertEqual(Availability.objects.count(), 1)
