from django import forms
from .models import TodoList, Task
from django.contrib.auth.forms import PasswordResetForm


class TodoListForm(forms.ModelForm):
    class Meta:
        model = TodoList
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-slate-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent backdrop-blur-sm',
                'placeholder': 'Enter list title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-slate-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent backdrop-blur-sm',
                'placeholder': 'Optional description...',
                'rows': 4
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter task title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Optional description...',
                'rows': 3
            })
        }

    def __init__(self, *args, **kwargs):
        self.todo_list = kwargs.pop('todo_list', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.todo_list:
            instance.todo_list = self.todo_list
        if commit:
            instance.save()
        return instance

class TodoListSearchForm(forms.Form):
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'search-input w-full pl-12 pr-4 py-4 bg-white/10 border border-white/20 rounded-xl text-white placeholder-slate-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-300 backdrop-blur-sm',
            'placeholder': 'Search your lists...'
        })
    )


from django.contrib.auth.forms import (
    PasswordResetForm, 
    SetPasswordForm, 
    AuthenticationForm
)
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomPasswordResetForm(PasswordResetForm):
    """Enhanced password reset form with better validation and styling"""
    
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
            'required': True,
        }),
        label='Email Address',
        help_text='Enter the email address associated with your account.'
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        logger.info(f"Validating email in form: {email}")
        
        if not email:
            raise ValidationError("Email address is required.")
            
        # Check if any user exists with this email (active or not)
        if not User.objects.filter(email__iexact=email).exists():
            logger.warning(f"No user found with email: {email}")
            # Don't reveal if email exists for security
            pass
        else:
            # Check if user is active
            active_users = User.objects.filter(email__iexact=email, is_active=True)
            if not active_users.exists():
                logger.warning(f"User exists but is inactive: {email}")
        
        return email
    
    def get_users(self, email):
        """Override to get active users and log the process"""
        active_users = User.objects.filter(
            email__iexact=email,
            is_active=True
        )
        
        logger.info(f"Found {active_users.count()} active users for email: {email}")
        
        # Return users who have usable passwords
        valid_users = []
        for user in active_users:
            if user.has_usable_password():
                valid_users.append(user)
                logger.info(f"Valid user for reset: {user.username}")
            else:
                logger.warning(f"User {user.username} has no usable password")
        
        return valid_users


class CustomSetPasswordForm(SetPasswordForm):
    """Enhanced set password form with strength validation"""
    
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your new password',
            'autocomplete': 'new-password',
        }),
        strip=False,
        help_text=(
            'Your password must contain at least 8 characters, including uppercase, '
            'lowercase, numbers, and special characters.'
        )
    )
    
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your new password',
            'autocomplete': 'new-password',
        }),
        strip=False,
        help_text='Enter the same password as above for verification.'
    )
    
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        
        if not password:
            return password
        
        errors = []
        
        # Length check
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        # Character type checks
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter.')
        
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter.')
        
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one number.')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).')
        
        # Common password patterns
        if password.lower() in ['password', '12345678', 'qwerty123']:
            errors.append('This password is too common. Please choose a more secure password.')
        
        if errors:
            logger.warning(f"Password validation failed: {errors}")
            raise ValidationError(errors)
        
        logger.info("Password passed all validation checks")
        return password
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("The two password fields didn't match.")
        
        return password2


class CustomAuthenticationForm(AuthenticationForm):
    """Enhanced login form with better styling"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username or Email',
            'autocomplete': 'username',
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })
    )


