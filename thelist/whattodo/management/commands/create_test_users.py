from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create test users for password reset testing'
    
    def handle(self, *args, **options):
        # Create test users
        test_users = [
            {
                'username': 'testuser1',
                'email': 'listnote07@gmail.com',
                'first_name': 'Test',
                'last_name': 'User One',
                'password': 'testpass123'
            },
            {
                'username': 'testuser2', 
                'email': 'listnote07@gmail.com',
                'first_name': 'Test',
                'last_name': 'User Two',
                'password': 'testpass456'
            }
        ]
        
        for user_data in test_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_active': True
                }
            )
            
            user.set_password(user_data['password'])
            user.save()
            
            action = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f'{action} user: {user.username} ({user.email})'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ Test users ready for password reset testing!'
            )
        )