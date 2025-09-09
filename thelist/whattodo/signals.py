from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile
import logging
from django.template.loader import render_to_string
from django.utils.html import strip_tags




logger = logging.getLogger(__name__)



from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging



# whattodo/signals.py

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created and instance.email:
        send_mail(
            subject="🎉 Welcome to Notes!",
            message=f"Hi {instance.first_name or instance.username},\n\nThanks for signing up! We're excited to have you 🚀",
            from_email=None,  # uses DEFAULT_FROM_EMAIL from settings.py
            recipient_list=[instance.email],
            fail_silently=False,
        )
