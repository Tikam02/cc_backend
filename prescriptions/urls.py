from django.urls import path
from . import views

urlpatterns = [
    path('api/auth/login/', views.login, name='login'),
    path('api/auth/verify/', views.verify_token, name='verify_token'),
    path('api/patients/', views.patients_list, name='patients_list'),
    path('api/prescriptions/', views.create_prescription, name='create_prescription'),
    path('api/prescriptions/public/', views.get_prescription_by_token, name='get_prescription_by_token'),
    path('api/reminders/', views.set_medication_reminder, name='set_medication_reminder'),
    path('test/', views.test_page, name='test_page'),
]