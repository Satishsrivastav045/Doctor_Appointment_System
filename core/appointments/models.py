from django.db import models
from accounts.models import Patient
from doctors.models import Doctor, Availability


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["availability"],
                name="unique_appointment_per_availability",
            )
        ]

    def __str__(self):
        return f"{self.patient} - {self.doctor}"
