from django.contrib import admin
from .models import ClinicStaff, Patient, Prescription, Medication

admin.site.register(ClinicStaff)
admin.site.register(Patient)
admin.site.register(Prescription)
admin.site.register(Medication)