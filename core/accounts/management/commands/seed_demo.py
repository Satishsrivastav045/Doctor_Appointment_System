from datetime import datetime, time, timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.timezone import localdate

from accounts.models import Patient, Role, User
from appointments.models import Appointment
from doctors.models import Availability, Doctor
from pharmacies.models import MedicineStock, Pharmacy


DEMO_PASSWORD = "demo12345"


class Command(BaseCommand):
    help = "Create demo users, doctors, slots, and appointments for a full product walkthrough."

    def handle(self, *args, **options):
        doctor_role, _ = Role.objects.get_or_create(role_name="doctor")
        patient_role, _ = Role.objects.get_or_create(role_name="patient")
        pharmacy_role, _ = Role.objects.get_or_create(role_name="pharmacy")

        patient_user = self._user(
            username="demo_patient",
            role=patient_role,
            email="patient.demo@doctorsaheb.test",
            first_name="Aarav Mehta",
        )
        patient, _ = Patient.objects.update_or_create(
            user=patient_user,
            defaults={"patient_name": "Aarav Mehta", "dob": "1998-08-14"},
        )

        doctor_specs = [
            {
                "username": "demo_dr_neha",
                "name": "Dr. Neha Sharma",
                "specialization": "General Physician",
                "phone_no": "9876543210",
                "email_id": "neha.sharma@doctorsaheb.test",
                "photo_url": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=500&q=80",
                "whatsapp_number": "919876543210",
                "consultation_fee": "500.00",
                "rating": "4.8",
                "review_count": 186,
                "hospital_name": "Seva Clinic",
                "district": "Varanasi",
                "city_or_block": "Pindra",
                "village_or_area": "Phoolpur",
                "full_address": "Seva Clinic, Phoolpur, Pindra, Varanasi",
                "latitude": "25.448425",
                "longitude": "82.857690",
                "is_emergency_available": True,
                "consultation_mode": "both",
                "slots": [(1, time(9, 30), time(10, 0)), (1, time(10, 30), time(11, 0)), (2, time(17, 0), time(17, 30))],
            },
            {
                "username": "demo_dr_rahul",
                "name": "Dr. Rahul Verma",
                "specialization": "Cardiologist",
                "phone_no": "9876501234",
                "email_id": "rahul.verma@doctorsaheb.test",
                "photo_url": "https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&w=500&q=80",
                "whatsapp_number": "919876501234",
                "consultation_fee": "900.00",
                "rating": "4.9",
                "review_count": 241,
                "hospital_name": "City Heart Care",
                "district": "Varanasi",
                "city_or_block": "Varanasi Urban",
                "village_or_area": "Lanka",
                "full_address": "City Heart Care, Lanka, Varanasi",
                "latitude": "25.267720",
                "longitude": "82.991258",
                "is_emergency_available": True,
                "consultation_mode": "offline",
                "slots": [(1, time(12, 0), time(12, 30)), (3, time(9, 0), time(9, 30)), (4, time(18, 0), time(18, 30))],
            },
            {
                "username": "demo_dr_aisha",
                "name": "Dr. Aisha Khan",
                "specialization": "Dermatologist",
                "phone_no": "9876512345",
                "email_id": "aisha.khan@doctorsaheb.test",
                "photo_url": "https://images.unsplash.com/photo-1594824476967-48c8b964273f?auto=format&fit=crop&w=500&q=80",
                "whatsapp_number": "919876512345",
                "consultation_fee": "700.00",
                "rating": "4.7",
                "review_count": 132,
                "hospital_name": "Skin Health Centre",
                "district": "Jaunpur",
                "city_or_block": "Kerakat",
                "village_or_area": "Thana Gaddi",
                "full_address": "Skin Health Centre, Thana Gaddi, Kerakat, Jaunpur",
                "latitude": "25.681020",
                "longitude": "82.835741",
                "is_emergency_available": False,
                "consultation_mode": "both",
                "slots": [(2, time(11, 0), time(11, 30)), (2, time(16, 0), time(16, 30)), (5, time(10, 0), time(10, 30))],
            },
            {
                "username": "demo_dr_kavya",
                "name": "Dr. Kavya Iyer",
                "specialization": "Gynecologist",
                "phone_no": "9876523456",
                "email_id": "kavya.iyer@doctorsaheb.test",
                "photo_url": "https://images.unsplash.com/photo-1651008376811-b90baee60c1f?auto=format&fit=crop&w=500&q=80",
                "whatsapp_number": "919876523456",
                "consultation_fee": "800.00",
                "rating": "4.8",
                "review_count": 159,
                "hospital_name": "Matrika Women's Clinic",
                "district": "Chandauli",
                "city_or_block": "Mughalsarai",
                "village_or_area": "Ali Nagar",
                "full_address": "Matrika Women's Clinic, Ali Nagar, Mughalsarai, Chandauli",
                "latitude": "25.280925",
                "longitude": "83.121257",
                "is_emergency_available": False,
                "consultation_mode": "offline",
                "slots": [(1, time(15, 0), time(15, 30)), (3, time(11, 30), time(12, 0)), (6, time(9, 30), time(10, 0))],
            },
        ]

        doctors = []
        for spec in doctor_specs:
            user = self._user(
                username=spec["username"],
                role=doctor_role,
                email=spec["email_id"],
                first_name=spec["name"],
            )
            doctor, _ = Doctor.objects.update_or_create(
                user=user,
                defaults={
                    "name": spec["name"],
                    "specialization": spec["specialization"],
                    "phone_no": spec["phone_no"],
                    "email_id": spec["email_id"],
                    "photo_url": spec["photo_url"],
                    "whatsapp_number": spec["whatsapp_number"],
                    "consultation_fee": spec["consultation_fee"],
                    "rating": spec["rating"],
                    "review_count": spec["review_count"],
                    "hospital_name": spec["hospital_name"],
                    "district": spec["district"],
                    "city_or_block": spec["city_or_block"],
                    "village_or_area": spec["village_or_area"],
                    "full_address": spec["full_address"],
                    "latitude": spec["latitude"],
                    "longitude": spec["longitude"],
                    "is_emergency_available": spec["is_emergency_available"],
                    "consultation_mode": spec["consultation_mode"],
                    "is_verified": True,
                },
            )
            doctors.append(doctor)
            self._slots(doctor, spec["slots"])

        self._appointments(patient, doctors)
        self._pharmacies(pharmacy_role)

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write("Patient login: demo_patient / demo12345")
        self.stdout.write("Doctor login: demo_dr_neha / demo12345")
        self.stdout.write("Pharmacy login: demo_pharmacy / demo12345")
        call_command("ensure_superuser")

    def _user(self, username, role, email, first_name):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "first_name": first_name, "role": role},
        )
        user.email = email
        user.first_name = first_name
        user.role = role
        user.set_password(DEMO_PASSWORD)
        user.save(update_fields=["email", "first_name", "role", "password"])
        return user

    def _slots(self, doctor, slot_specs):
        today = localdate()
        for day_offset, start_time, end_time in slot_specs:
            Availability.objects.update_or_create(
                doctor=doctor,
                available_date=today + timedelta(days=day_offset),
                start_time=start_time,
                defaults={"end_time": end_time, "is_booked": False},
            )

    def _appointments(self, patient, doctors):
        today = localdate()
        appointment_specs = [
            (doctors[0], today + timedelta(days=1), time(9, 30), "confirmed"),
            (doctors[1], today + timedelta(days=1), time(12, 0), "pending"),
            (doctors[2], today - timedelta(days=7), time(11, 0), "cancelled"),
        ]

        for doctor, appointment_date, start_time, status in appointment_specs:
            end_time = (datetime.combine(appointment_date, start_time) + timedelta(minutes=30)).time()
            slot, _ = Availability.objects.update_or_create(
                doctor=doctor,
                available_date=appointment_date,
                start_time=start_time,
                defaults={
                    "end_time": end_time,
                    "is_booked": status != "cancelled",
                },
            )
            Appointment.objects.update_or_create(
                patient=patient,
                doctor=doctor,
                availability=slot,
                defaults={"appointment_date": appointment_date, "status": status},
            )

    def _pharmacies(self, pharmacy_role):
        user = self._user(
            username="demo_pharmacy",
            role=pharmacy_role,
            email="pharmacy.demo@doctorsaheb.test",
            first_name="Seva Medical Store",
        )
        pharmacy, _ = Pharmacy.objects.update_or_create(
            user=user,
            defaults={
                "shop_name": "Seva Medical Store",
                "owner_name": "Ramesh Gupta",
                "phone_no": "9876509876",
                "whatsapp_number": "919876509876",
                "license_number": "UP-VNS-2026-4451",
                "district": "Varanasi",
                "city_or_block": "Pindra",
                "village_or_area": "Phoolpur",
                "full_address": "Seva Medical Store, Main Road, Phoolpur, Pindra, Varanasi",
                "opening_time": time(8, 0),
                "closing_time": time(22, 0),
                "is_verified": True,
                "is_open_now": True,
            },
        )

        medicine_specs = [
            ("Paracetamol", "Dolo", "500mg", "Tablet", "28.00", 42, False),
            ("Cetirizine", "Cetzine", "10mg", "Tablet", "22.00", 30, False),
            ("Amoxicillin", "Mox", "500mg", "Capsule", "118.00", 12, True),
            ("ORS", "Electral", "21.8g", "Sachet", "24.00", 25, False),
        ]
        for name, brand, strength, form, price, quantity, prescription_required in medicine_specs:
            MedicineStock.objects.update_or_create(
                pharmacy=pharmacy,
                medicine_name=name,
                brand_name=brand,
                defaults={
                    "strength": strength,
                    "form": form,
                    "price": price,
                    "quantity": quantity,
                    "prescription_required": prescription_required,
                },
            )
