from rest_framework import serializers
from .models import ClinicStaff, Patient, Prescription, Medication, MedicationReminder

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)

class ClinicStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicStaff
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'clinic_name', 'role']
        read_only_fields = ['id']

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'phone_number', 'created_at']
        read_only_fields = ['id', 'created_at']

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ['id', 'name', 'dosage', 'frequency', 'duration', 'instructions']
        read_only_fields = ['id']

class PrescriptionSerializer(serializers.ModelSerializer):
    medications = MedicationSerializer(many=True)
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone_number', read_only=True)
    
    class Meta:
        model = Prescription
        fields = ['id', 'patient', 'patient_name', 'patient_phone', 'medications', 
                  'token', 'created_at', 'link_sent_via']
        read_only_fields = ['id', 'token', 'created_at']

class CreatePrescriptionSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField()
    medications = MedicationSerializer(many=True)
    send_via = serializers.ChoiceField(choices=['whatsapp', 'sms'])

class MedicationReminderSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source='medication.name', read_only=True)
    
    class Meta:
        model = MedicationReminder
        fields = ['id', 'medication', 'medication_name', 'reminder_time', 'is_active']
        read_only_fields = ['id']