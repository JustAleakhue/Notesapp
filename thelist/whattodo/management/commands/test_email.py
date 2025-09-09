from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email configuration'
    
    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address to send test to')
    
    def handle(self, *args, **options):
        email = options.get('email') or 'listnote07@gmail.com'
        
        self.stdout.write(f'Testing email configuration...')
        self.stdout.write(f'Backend: {settings.EMAIL_BACKEND}')
        
        if hasattr(settings, 'EMAIL_HOST_USER'):
            self.stdout.write(f'From: {settings.EMAIL_HOST_USER}')
        
        try:
            result = send_mail(
                subject='Django Email Test',
                message='This is a test email from Django management command.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Email sent successfully to {email}! Result: {result}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Email failed: {str(e)}')
            )