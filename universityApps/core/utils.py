import random
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(email, code):
    subject = 'رمز التحقق من البريد الإلكتروني'
    from_email = settings.DEFAULT_FROM_EMAIL  # يفضل استخدام from settings
    to = [email]

    # نسخة نصية احتياطية
    text_content = f'رمز التحقق الخاص بك هو: {code}'

    # نسخة HTML من قالب مخصص
    html_content = render_to_string('emails/verification_code.html', {'code': code})

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
