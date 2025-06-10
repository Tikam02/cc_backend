from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from datetime import datetime, timedelta

class ClinicStaff(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    clinic_name = models.CharField(max_length=200, blank=True)
    role = models.CharField(max_length=50, choices=[
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('pharmacist', 'Pharmacist'),
    ], default='doctor')
    
    # Fix reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='clinic_staff_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='clinic_staff_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username']

class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    created_by = models.ForeignKey(ClinicStaff, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['phone_number', 'created_by']

class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    created_by = models.ForeignKey(ClinicStaff, on_delete=models.SET_NULL, null=True)
    token = models.CharField(max_length=100, unique=True)
    token_expiry = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    link_sent_via = models.CharField(max_length=20, choices=[
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
    ], blank=True)
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())
        if not self.token_expiry:
            self.token_expiry = datetime.now() + timedelta(days=7)
        super().save(*args, **kwargs)
    
    @property
    def is_token_valid(self):
        return datetime.now() < self.token_expiry

class Medication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class MedicationReminder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='reminders')
    reminder_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)