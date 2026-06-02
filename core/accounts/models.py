
from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    role_name = models.CharField(max_length=20)

    def __str__(self):
        return self.role_name


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    patient_name = models.CharField(max_length=150)
    dob = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.patient_name or self.user.username
