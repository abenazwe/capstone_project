# views.py
from urllib.parse import urlencode
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.validators import RegexValidator


def send_verification_email(user, verification_token):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    verification_link = f'http://127.0.0.1:8000/api/verify?{urlencode({"uid": uid})}'

    subject = 'Verify your email address'
    message = f'Click the following link to verify your email: {verification_link}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)


email_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
    message='Enter a valid email address.',
    code='invalid_email'
)

password_validator = RegexValidator(
    regex=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[*()\[\]@$!%#?&])[A-Za-z\d*()\[\]@$!%#?&]{8,}$',
    message='Password must be at least 8 characters long and include at least one letter, one digit, and one special character.',
    code='invalid_password'
    
)
