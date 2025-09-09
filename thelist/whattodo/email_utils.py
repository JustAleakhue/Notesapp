# whattodo/email_utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


def send_welcome_email(user):
    """
    Send welcome email to newly registered users
    This function is called only once when a user first registers
    """
    try:
        # Email subject
        subject = f'🎉 Welcome to {getattr(settings, "SITE_NAME", "Notes")}!'
        
        # Email context
        context = {
            'user': user,
            'user_name': user.first_name or user.username,
            'app_name': getattr(settings, 'SITE_NAME', 'Notes'),
            'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
            'login_url': f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/login/",
            'dashboard_url': f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/dashboard/",
        }
        
        # Render HTML email
        html_message = render_to_string('emails/welcome_email.html', context)
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        
        # Attach HTML version
        email.attach_alternative(html_message, "text/html")
        
        # Send email
        email.send(fail_silently=False)
        
        logger.info(f"✅ Welcome email sent successfully to {user.email}")
        print(f"✅ Welcome email sent to {user.email}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send welcome email to {user.email}: {str(e)}")
        print(f"❌ Failed to send welcome email to {user.email}: {str(e)}")
        return False


def send_password_reset_email(user, reset_url):
    """
    Send custom password reset email
    """
    try:
        subject = f'Reset Your {getattr(settings, "SITE_NAME", "Notes")} Password'
        
        context = {
            'user': user,
            'user_name': user.first_name or user.username,
            'app_name': getattr(settings, 'SITE_NAME', 'Notes'),
            'reset_url': reset_url,
            'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
        }
        
        html_message = render_to_string('emails/password_reset_email.html', context)
        plain_message = strip_tags(html_message)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"✅ Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send password reset email to {user.email}: {str(e)}")
        return False


def test_email_configuration():
    """
    Test function to check if email configuration is working
    Call this in Django shell: python manage.py shell
    >>> from whattodo.email_utils import test_email_configuration
    >>> test_email_configuration()
    """
    try:
        from django.core.mail import send_mail
        
        send_mail(
            'Email Configuration Test',
            'This is a test email to verify email configuration.',
            settings.DEFAULT_FROM_EMAIL,
            ['listnote07@gmail.com'],  # Replace with your email for testing
            fail_silently=False,
        )
        print("✅ Email configuration test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Email configuration test failed: {str(e)}")
        return False