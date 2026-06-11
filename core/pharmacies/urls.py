from django.urls import path

from .views import medicine_search, pharmacy_dashboard, upsert_medicine

urlpatterns = [
    path("pharmacies/", medicine_search, name="medicine_search"),
    path("pharmacy-dashboard/", pharmacy_dashboard, name="pharmacy_dashboard"),
    path("pharmacy/medicines/add/", upsert_medicine, name="add_medicine"),
    path("pharmacy/medicines/<int:medicine_id>/edit/", upsert_medicine, name="edit_medicine"),
]
