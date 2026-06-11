from django.contrib import admin

from .models import MedicineStock, Pharmacy


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ("shop_name", "owner_name", "phone_no", "district", "is_verified", "is_open_now")
    list_filter = ("is_verified", "is_open_now", "district")
    search_fields = ("shop_name", "owner_name", "phone_no", "license_number", "district")


@admin.register(MedicineStock)
class MedicineStockAdmin(admin.ModelAdmin):
    list_display = ("medicine_name", "brand_name", "pharmacy", "price", "quantity", "prescription_required")
    list_filter = ("prescription_required", "pharmacy__district")
    search_fields = ("medicine_name", "brand_name", "pharmacy__shop_name")

# Register your models here.
