from django.urls import path
from .views import register, user_login, user_logout, patient_dashboard, doctor_dashboard

urlpatterns = [
    path('register/', register),
    path('login/', user_login),
    path('logout/', user_logout),
    path('patient-dashboard/', patient_dashboard, name='patient_dashboard'),
    path('doctor-dashboard/', doctor_dashboard, name='doctor_dashboard'),
]