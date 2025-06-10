import jwt
from django.conf import settings
from datetime import datetime, timedelta
from twilio.rest import Client

def generate_jwt_token(user_id):
    payload = {
        'user_id': str(user_id),
        'exp': datetime.utcnow() + settings.JWT_EXPIRATION_DELTA
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def send_prescription_link(phone_number, link, send_via='whatsapp'):
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN]):
        print("Twilio credentials not configured")
        return
    
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    message_body = f"Your prescription is ready! Click here to view: {link}"
    
    try:
        if send_via == 'whatsapp':
            from_number = settings.TWILIO_WHATSAPP_NUMBER
            to_number = f"whatsapp:{phone_number}"
        else:
            from_number = settings.TWILIO_PHONE_NUMBER
            to_number = phone_number
        
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        
        print(f"Message sent: {message.sid}")
        return message.sid
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        raise