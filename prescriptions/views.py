from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Patient, Prescription, Medication, MedicationReminder
from .serializers import *
from .utils import generate_jwt_token, decode_jwt_token, send_prescription_link
import jwt
from django.shortcuts import render


User = get_user_model()

# @api_view(['POST'])
# def login(request):
#     serializer = LoginSerializer(data=request.data)
#     if serializer.is_valid():
#         phone_number = serializer.validated_data['phone_number']
#         otp = serializer.validated_data['otp']
        
#         if otp != settings.CONSTANT_OTP:
#             return Response({'error': 'Invalid OTP'}, status=status.HTTP_401_UNAUTHORIZED)
        
#         staff, created = User.objects.get_or_create(
#             phone_number=phone_number,
#             defaults={'username': phone_number}
#         )
        
#         token = generate_jwt_token(staff.id)
        
#         return Response({
#             'token': token,
#             'staff': ClinicStaffSerializer(staff).data,
#             'is_new_user': created
#         })
    
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']
        
        if otp != settings.CONSTANT_OTP:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Fix: Use ClinicStaff directly
        staff, created = ClinicStaff.objects.get_or_create(
            phone_number=phone_number,
            defaults={'username': phone_number}
        )
        
        token = generate_jwt_token(staff.id)
        
        return Response({
            'token': token,
            'staff': ClinicStaffSerializer(staff).data,
            'is_new_user': created
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def verify_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token = auth_header.split(' ')[1]
    user_id = decode_jwt_token(token)
    
    if user_id:
        try:
            staff = User.objects.get(id=user_id)
            return Response({'valid': True, 'staff': ClinicStaffSerializer(staff).data})
        except User.DoesNotExist:
            pass
    
    return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'POST'])
def patients_list(request):
    user_id = authenticate_request(request)
    if not user_id:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == 'GET':
        patients = Patient.objects.filter(created_by_id=user_id)
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by_id=user_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_prescription(request):
    user_id = authenticate_request(request)
    if not user_id:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer = CreatePrescriptionSerializer(data=request.data)
    if serializer.is_valid():
        patient_id = serializer.validated_data['patient_id']
        medications_data = serializer.validated_data['medications']
        send_via = serializer.validated_data['send_via']
        
        try:
            patient = Patient.objects.get(id=patient_id, created_by_id=user_id)
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        prescription = Prescription.objects.create(
            patient=patient,
            created_by_id=user_id,
            link_sent_via=send_via
        )
        
        for med_data in medications_data:
            Medication.objects.create(
                prescription=prescription,
                **med_data
            )
        
        link = f"{settings.PRESCRIPTION_LINK_BASE_URL}?token={prescription.token}"
        
        try:
            send_prescription_link(patient.phone_number, link, send_via)
        except Exception as e:
            print(f"Failed to send message: {str(e)}")
        
        return Response(PrescriptionSerializer(prescription).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_prescription_by_token(request):
    token = request.query_params.get('token')
    if not token:
        return Response({'error': 'Token required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        prescription = Prescription.objects.get(token=token)
        if not prescription.is_token_valid:
            return Response({'error': 'Token expired'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(PrescriptionSerializer(prescription).data)
    except Prescription.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def set_medication_reminder(request):
    serializer = MedicationReminderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def authenticate_request(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    return decode_jwt_token(token)


def test_page(request):
    return render(request, 'test.html')


