from django.db import models
from accounts.models import User


class Doctor(models.Model):
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
