from django.urls import path
from .views import ai_features, book_appointment, update_status, cancel_appointment

urlpatterns = [
    path('ai-features/', ai_features, name='ai_features'),
    path('book/<int:doctor_id>/', book_appointment, name='book_appointment'),
    path('update/<int:id>/<str:status>/', update_status, name='update_status'),
    path('cancel/<int:id>/', cancel_appointment, name='cancel_appointment'),
]
