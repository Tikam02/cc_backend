# Care Clinic API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require Bearer token in header:
```
Authorization: Bearer YOUR_TOKEN_HERE
```

---

## 1. Login
**POST** `/api/auth/login/`

**Request:**
```json
{
    "phone_number": "+919876543210",
    "otp": "123456"
}
```

**Response:**
```json
{
    "token": "eyJhbGci...",
    "staff": {
        "id": 1,
        "phone_number": "+919876543210",
        "first_name": "",
        "last_name": "",
        "clinic_name": "",
        "role": "doctor"
    },
    "is_new_user": true
}
```

**Next.js Example:**
```javascript
const login = async () => {
  const res = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      phone_number: '+919876543210',
      otp: '123456'
    })
  });
  const data = await res.json();
  localStorage.setItem('token', data.token);
  return data;
};
```

---

## 2. Verify Token
**GET** `/api/auth/verify/`

**Headers Required:** `Authorization: Bearer TOKEN`

**Response:**
```json
{
    "valid": true,
    "staff": {
        "id": 1,
        "phone_number": "+919876543210",
        "role": "doctor"
    }
}
```

---

## 3. List Patients
**GET** `/api/patients/`

**Headers Required:** `Authorization: Bearer TOKEN`

**Response:**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "John Doe",
        "phone_number": "+919876543210",
        "created_at": "2024-01-15T10:30:00Z"
    }
]
```

---

## 4. Add Patient
**POST** `/api/patients/`

**Headers Required:** `Authorization: Bearer TOKEN`

**Request:**
```json
{
    "name": "John Doe",
    "phone_number": "+919876543210"
}
```

**Response:** Same as single patient object above

**Next.js Example:**
```javascript
const addPatient = async (name, phone) => {
  const token = localStorage.getItem('token');
  const res = await fetch('http://localhost:8000/api/patients/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ name, phone_number: phone })
  });
  return await res.json();
};
```

---

## 5. Create Prescription
**POST** `/api/prescriptions/`

**Headers Required:** `Authorization: Bearer TOKEN`

**Request:**
```json
{
    "patient_id": "550e8400-e29b-41d4-a716-446655440000",
    "send_via": "sms",
    "medications": [
        {
            "name": "Paracetamol",
            "dosage": "500mg",
            "frequency": "Twice daily",
            "duration": "3 days",
            "instructions": "After meals"
        },
        {
            "name": "Amoxicillin",
            "dosage": "250mg",
            "frequency": "Three times daily",
            "duration": "7 days",
            "instructions": "Complete the course"
        }
    ]
}
```

**Response:**
```json
{
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "patient": "550e8400-e29b-41d4-a716-446655440000",
    "patient_name": "John Doe",
    "patient_phone": "+919876543210",
    "medications": [...],
    "token": "abc123-def456-ghi789",
    "created_at": "2024-01-15T11:00:00Z",
    "link_sent_via": "sms"
}
```

---

## 6. Get Prescription (Public - No Auth)
**GET** `/api/prescriptions/public/?token=TOKEN`

**No Authentication Required**

**Example URL:**
```
http://localhost:8000/api/prescriptions/public/?token=abc123-def456-ghi789
```

**Response:** Same as prescription object above

**Next.js Example:**
```javascript
const getPrescription = async (token) => {
  const res = await fetch(`http://localhost:8000/api/prescriptions/public/?token=${token}`);
  return await res.json();
};
```

---

## 7. Set Medication Reminder
**POST** `/api/reminders/`

**Request:**
```json
{
    "medication": "770e8400-e29b-41d4-a716-446655440002",
    "reminder_time": "09:00:00"
}
```

**Response:**
```json
{
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "medication": "770e8400-e29b-41d4-a716-446655440002",
    "medication_name": "Paracetamol",
    "reminder_time": "09:00:00",
    "is_active": true
}
```

---

## Testing Workflow

1. **Login first** - Get token
2. **Add patients** - Use token in header
3. **Create prescription** - Use patient ID from step 2
4. **Share link** - Use token from prescription response

## Common Values for Testing

**Phone Numbers:**
- `+919876543210`
- `+919123456789`
- `+919999999999`

**OTP:** Always `123456` for local testing

**Medicine Examples:**
- Paracetamol 500mg, Twice daily, 3 days
- Amoxicillin 250mg, Three times daily, 7 days
- Omeprazole 20mg, Once daily, 14 days
- Cetirizine 10mg, Once daily, 5 days

**Send Via Options:** `sms` or `whatsapp`

## Next.js API Service
```javascript
// api.js
const API_BASE = 'http://localhost:8000';

const getHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('token')}`
});

export const api = {
  login: (phone, otp) => 
    fetch(`${API_BASE}/api/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone_number: phone, otp })
    }).then(r => r.json()),
    
  getPatients: () =>
    fetch(`${API_BASE}/api/patients/`, { headers: getHeaders() })
      .then(r => r.json()),
      
  addPatient: (name, phone) =>
    fetch(`${API_BASE}/api/patients/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ name, phone_number: phone })
    }).then(r => r.json()),
    
  createPrescription: (data) =>
    fetch(`${API_BASE}/api/prescriptions/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    }).then(r => r.json()),
    
  getPrescription: (token) =>
    fetch(`${API_BASE}/api/prescriptions/public/?token=${token}`)
      .then(r => r.json())
};
```