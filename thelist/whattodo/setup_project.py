#!/usr/bin/env python
"""
Complete setup script for Django password reset functionality
Run this after creating your Django project and app
"""
import os
import sys
import django
from pathlib import Path

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thelist.settings')
    django.setup()

def create_env_file():
    """Create .env file with default settings"""
    env_content = """# Django Password Reset Configuration
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Email Settings for Pre-Production
SEND_REAL_EMAILS=True
EMAIL_HOST_USER=listnote07@gmail.com
EMAIL_HOST_PASSWORD=ykaj wumo gesi ijzq
DEFAULT_FROM_EMAIL=listnote07@gmail.com

# Database (PostgreSQL - optional)
# DB_NAME=whattodo_db
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=5432
"""

    env_path = Path('.env')
    if not env_path.exists():
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("ℹ️  .env file already exists")

def run_migrations():
    """Run Django migrations"""
    from django.core.management import execute_from_command_line

    print("Running migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    print("✅ Migrations completed")

def create_superuser():
    """Create superuser if none exists"""
    from django.contrib.auth.models import User

    if not User.objects.filter(is_superuser=True).exists():
        print("Creating superuser...")
        User.objects.create_superuser(
            username='admin',
            email='listnote07@gmail.com',
            password='admin123'
        )
        print("✅ Superuser created: admin/admin123")
    else:
        print("ℹ️  Superuser already exists")

def create_test_users():
    """Create test users for password reset"""
    from django.contrib.auth.models import User

    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'listnote07@gmail.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )

    test_user.set_password('testpass123')
    test_user.save()

    action = "Created" if created else "Updated"
    print(f"✅ {action} test user: testuser/testpass123 (listnote07@gmail.com)")

def test_email_config():
    """Test email configuration"""
    from django.core.mail import send_mail
    from django.conf import settings

    print(f"Email backend: {settings.EMAIL_BACKEND}")

    try:
        result = send_mail(
            'Django Setup Test',
            'Your Django password reset setup is working!',
            settings.DEFAULT_FROM_EMAIL,
            ['listnote07@gmail.com'],
            fail_silently=False,
        )
        print(f"✅ Test email sent successfully! Result: {result}")
        print("Check your Gmail inbox.")
    except Exception as e:
        print(f"❌ Email test failed: {e}")

def main():
    """Main setup function"""
    print("🚀 Setting up Django Password Reset...")

    # Setup environment
    create_env_file()
    setup_django()

    # Database setup
    run_migrations()
    create_superuser()
    create_test_users()

    # Test email
    test_email_config()

    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Run: python manage.py runserver")
    print("2. Visit: http://127.0.0.1:8000/debug/email-config/")
    print("3. Test: http://127.0.0.1:8000/password-reset/")
    print("4. Use email: listnote07@gmail.com")
    print("5. Check your Gmail inbox!")

if __name__ == '__main__':
    main()