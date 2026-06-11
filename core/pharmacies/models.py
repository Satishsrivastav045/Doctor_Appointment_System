from django.db import models

from accounts.models import User


class Pharmacy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="pharmacy_profile")
    shop_name = models.CharField(max_length=180)
    owner_name = models.CharField(max_length=150, blank=True)
    phone_no = models.CharField(max_length=15, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    license_number = models.CharField(max_length=80, blank=True)
    district = models.CharField(max_length=100, blank=True)
    city_or_block = models.CharField(max_length=100, blank=True)
    village_or_area = models.CharField(max_length=120, blank=True)
    full_address = models.TextField(blank=True)
    opening_time = models.TimeField(blank=True, null=True)
    closing_time = models.TimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_open_now = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def location_label(self):
        return ", ".join(
            item for item in [self.village_or_area, self.city_or_block, self.district] if item
        )

    def __str__(self):
        return self.shop_name


class MedicineStock(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name="medicines")
    medicine_name = models.CharField(max_length=180)
    brand_name = models.CharField(max_length=180, blank=True)
    strength = models.CharField(max_length=80, blank=True)
    form = models.CharField(max_length=80, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)
    prescription_required = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["medicine_name"]

    @property
    def is_available(self):
        return self.quantity > 0

    def __str__(self):
        return f"{self.medicine_name} - {self.pharmacy.shop_name}"

# Create your models here.
