from django.db import models
from accounts.models import User


class Doctor(models.Model):
    CONSULTATION_MODES = [
        ("offline", "Offline"),
        ("online", "Online"),
        ("both", "Online and Offline"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    phone_no = models.CharField(max_length=15, blank=True)
    email_id = models.EmailField(blank=True)
    photo_url = models.URLField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    review_count = models.PositiveIntegerField(default=0)
    hospital_name = models.CharField(max_length=160, blank=True)
    district = models.CharField(max_length=100, blank=True)
    city_or_block = models.CharField(max_length=100, blank=True)
    village_or_area = models.CharField(max_length=120, blank=True)
    full_address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_emergency_available = models.BooleanField(default=False)
    consultation_mode = models.CharField(max_length=20, choices=CONSULTATION_MODES, default="offline")
    is_verified = models.BooleanField(default=False)

    @property
    def location_label(self):
        return ", ".join(
            item for item in [self.village_or_area, self.city_or_block, self.district] if item
        )

    def __str__(self):
        return self.name or self.user.username


class Availability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    available_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    is_booked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.end_time is None:
            self.end_time = self.start_time
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.doctor} - {self.available_date} {self.start_time}-{self.end_time}"
