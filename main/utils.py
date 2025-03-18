from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(pending_user):
    """Отправляет письмо с кодом подтверждения"""
    subject = 'Ваш код подтверждения'
    plain_message = f'Ваш код подтверждения: {pending_user.verification_code}'
    html_message = f'''
        <p>Ваш код подтверждения:</p>
        <p style="font-size: 24px; font-weight: bold;">{pending_user.verification_code}</p>
    '''
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [pending_user.email],
        html_message=html_message,
        fail_silently=False,
    )
