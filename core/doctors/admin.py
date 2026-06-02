from django.contrib import admin
from .models import Doctor, Availability


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "hospital_name",
        "specialization",
        "district",
        "city_or_block",
        "is_verified",
        "is_emergency_available",
        "consultation_mode",
    )
    list_filter = ("is_verified", "is_emergency_available", "consultation_mode", "district", "specialization")
    search_fields = (
        "name",
        "hospital_name",
        "specialization",
        "district",
        "city_or_block",
        "village_or_area",
        "phone_no",
    )
    list_editable = ("is_verified", "is_emergency_available")


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ("doctor", "available_date", "start_time", "end_time", "is_booked")
    list_filter = ("is_booked", "available_date")
    search_fields = ("doctor__name", "doctor__hospital_name")
