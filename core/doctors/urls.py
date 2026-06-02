from django.urls import path
from .views import doctor_list, doctor_detail, manage_availability, edit_availability, delete_availability

urlpatterns = [
    path('', doctor_list),      # ⭐ ye add karo (home page)
    path('doctors/', doctor_list),
    path('doctors/<int:doctor_id>/', doctor_detail, name='doctor_detail'),
    path('doctor/availability/', manage_availability, name='manage_availability'),
    path('doctor/availability/<int:slot_id>/edit/', edit_availability, name='edit_availability'),
    path('doctor/availability/<int:slot_id>/delete/', delete_availability, name='delete_availability'),
]
