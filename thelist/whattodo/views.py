from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.urls import reverse_lazy
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q
import re
import json
from .forms import TodoListForm, TaskForm
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import TodoList  
import logging
from django.contrib import messages
from .models import TodoList, Task
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django import forms
import traceback
from django.db.models.signals import post_save
from django.dispatch import receiver


def index(request):
    """Home page view"""
    return render(request, 'whattodo/index.html')

@csrf_protect
@never_cache
def signup_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('whattodo:my_lists')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        errors = []

        # Username validation
        if len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        elif len(username) > 30:
            errors.append('Username must be less than 30 characters.')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores.')
        elif User.objects.filter(username=username).exists():
            errors.append('Username already exists.')

        # Email validation
        if not email:
            errors.append('Email is required.')
        else:
            try:
                validate_email(email)
                if User.objects.filter(email=email).exists():
                    errors.append('Email already exists.')
            except ValidationError:
                errors.append('Please enter a valid email address.')

        # Password validation
        if len(password1) < 8:
            errors.append('Password must be at least 8 characters long.')
        elif password1 != password2:
            errors.append('Passwords do not match.')
        elif not re.search(r'[A-Za-z]', password1) or not re.search(r'\d', password1):
            errors.append('Password must contain both letters and numbers.')

        # Name validation
        if not first_name:
            errors.append('First name is required.')
        elif len(first_name) > 30:
            errors.append('First name must be less than 30 characters.')

        if last_name and len(last_name) > 30:
            errors.append('Last name must be less than 30 characters.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'whattodo/signup.html', {
                'form_data': {
                    'username': username,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                }
            })

        try:
            # ✅ Only create User, let signals handle UserProfile + email
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )

            login(request, user)
            messages.success(request, f'Welcome to Notes, {first_name or username}! Your account has been created successfully.')
            return redirect('whattodo:my_lists')

        except IntegrityError:
            messages.error(request, 'An error occurred while creating your account. Please try again.')
            return render(request, 'whattodo/signup.html', {
                'form_data': {
                    'username': username,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                }
            })

    return render(request, 'whattodo/signup.html')





@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created and instance.email:
        send_mail(
            subject="🎉 Welcome to Notes!",
            message=f"Hi {instance.username},\n\nThanks for signing up! We're excited to have you 🚀",
            from_email=None,
            recipient_list=[instance.email],
            fail_silently=False,
        )


@csrf_protect
@never_cache
def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('whattodo:my_lists')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')
        
        if not username or not password:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'whattodo/login.html', {'username': username})
        
        # Try to authenticate with username first
        user = authenticate(request, username=username, password=password)
        
        # If authentication failed, try with email
        if user is None:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None and user.is_active:
            login(request, user)
            # Set session expiry based on remember_me
            if not remember_me:
                request.session.set_expiry(0)  # Session expires when browser closes
            else:
                request.session.set_expiry(1209600)  # 2 weeks
            
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # Redirect to next page if provided
            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('whattodo:my_lists')
        else:
            messages.error(request, 'Invalid username/email or password.')
        
        return render(request, 'whattodo/login.html', {'username': username})
    
    return render(request, 'whattodo/login.html')

@csrf_protect
def logout_view(request):
    """User logout view"""
    if request.user.is_authenticated:
        user_name = request.user.first_name or request.user.username
        logout(request)
        messages.success(request, f'Goodbye, {user_name}! You have been logged out successfully.')
    return redirect('whattodo:login')



@login_required
def my_lists_view(request):
    """View all user's todo lists with filtering and search - Main list view"""
    search_query = request.GET.get('search', '')
    filter_by = request.GET.get('filter', 'all')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Get all lists for the current user
    todo_lists = TodoList.objects.filter(user=request.user)
    
    # Apply search filter
    if search_query:
        todo_lists = todo_lists.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Apply status filter
    if filter_by == 'completed':
        todo_lists = todo_lists.filter(is_completed=True)
    elif filter_by == 'active':
        todo_lists = todo_lists.filter(is_completed=False)
    elif filter_by == 'high_priority':
        # Filter for lists with many incomplete tasks (simulate high priority)
        pass  # Can be implemented based on task counts
    
    # Apply sorting
    valid_sort_fields = ['-created_at', 'created_at', '-updated_at', 'updated_at', 
                        'title', '-title']
    if sort_by in valid_sort_fields:
        todo_lists = todo_lists.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(todo_lists, 15)  # 15 lists per page to match template
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'filter_by': filter_by,
        'sort_by': sort_by,
        'total_lists': TodoList.objects.filter(user=request.user).count(),
        'completed_lists': TodoList.objects.filter(user=request.user, is_completed=True).count(),
    }
    
    return render(request, 'whattodo/my_lists.html', context)

@login_required
def create_list_view(request):
    if request.method == 'POST':
        form = TodoListForm(request.POST, user=request.user)
        if form.is_valid():
            todo_list = form.save()
            messages.success(request, f'List "{todo_list.title}" created successfully!')
            return redirect('whattodo:list_detail', pk=todo_list.pk)
    else:
        form = TodoListForm(user=request.user)
    
    return render(request, 'whattodo/create_list.html', {'form': form})

@login_required
def list_detail_view(request, pk):
    """View a specific todo list with its tasks"""
    todo_list = get_object_or_404(TodoList, pk=pk, user=request.user)
    
    # Get tasks with filtering and sorting
    search_task = request.GET.get('search_task', '')
    filter_tasks = request.GET.get('filter_tasks', 'all')
    sort_tasks = request.GET.get('sort_tasks', 'created_at')
    
    tasks = todo_list.tasks.all()
    
    # Apply task search
    if search_task:
        tasks = tasks.filter(
            Q(title__icontains=search_task) | 
            Q(description__icontains=search_task)
        )
    
    # Apply task filter
    if filter_tasks == 'completed':
        tasks = tasks.filter(is_completed=True)
    elif filter_tasks == 'pending':
        tasks = tasks.filter(is_completed=False)
    
    # Apply task sorting
    valid_task_sorts = ['created_at', '-created_at', 'title', '-title']
    if sort_tasks in valid_task_sorts:
        tasks = tasks.order_by(sort_tasks)
    
    # Get task statistics
    total_tasks = todo_list.tasks.count()
    completed_tasks = todo_list.tasks.filter(is_completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    
    context = {
        'todo_list': todo_list,
        'tasks': tasks,
        'search_task': search_task,
        'filter_tasks': filter_tasks,
        'sort_tasks': sort_tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
    }
    
    return render(request, 'whattodo/list_detail.html', context)

@login_required
def edit_list_view(request, pk):
    """Edit an existing todo list"""
    todo_list = get_object_or_404(TodoList, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TodoListForm(request.POST, instance=todo_list, user=request.user)
        if form.is_valid():
            todo_list = form.save()
            messages.success(request, f'List "{todo_list.title}" updated successfully!')
            return redirect('whattodo:list_detail', pk=todo_list.pk)
    else:
        form = TodoListForm(instance=todo_list, user=request.user)
    
    return render(request, 'whattodo/edit_list.html', {'form': form, 'todo_list': todo_list})

@login_required
@require_http_methods(["POST"])
def delete_list_view(request, pk):
    """Delete a todo list - Enhanced with confirmation"""
    todo_list = get_object_or_404(TodoList, pk=pk, user=request.user)
    list_title = todo_list.title
    
    # Check for confirmation parameter
    confirmed = request.POST.get('confirmed', 'false').lower() == 'true'
    
    if not confirmed:
        # Return confirmation request for AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'requires_confirmation': True,
                'message': f'Are you sure you want to delete "{list_title}"? This will also delete all {todo_list.total_tasks} tasks.',
                'list_title': list_title,
                'task_count': todo_list.total_tasks
            })
        else:
            # For non-AJAX requests, redirect to confirmation page
            return render(request, 'whattodo/my_lists.html', {
                'todo_list': todo_list
            })
    
    try:
        todo_list.delete()
        
        # Check if request expects JSON response (AJAX)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'List "{list_title}" and all its tasks deleted successfully!'
            })
        else:
            messages.success(request, f'List "{list_title}" and all its tasks deleted successfully!')
            return redirect('whattodo:my_lists')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'message': 'An error occurred while deleting the list.'
            })
        else:
            messages.error(request, 'An error occurred while deleting the list.')
            return redirect('whattodo:my_lists')

# Task Views



@login_required
@require_POST
def toggle_list_completion(request, list_id):
    todo_list = get_object_or_404(TodoList, id=list_id, user=request.user)
    total = todo_list.total_tasks
    completed = todo_list.completed_tasks
    new_status = completed < total
    todo_list.tasks.update(is_completed=new_status)
    return JsonResponse({'success': True, 'completed': new_status})


@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def delete_list(request, pk):
    """
    Delete a todo list
    """
    try:
        # Get the list item and ensure it belongs to the current user
        todo_list = get_object_or_404(TodoList, pk=pk, user=request.user)
        list_title = todo_list.title  # Store title before deletion
        
        # Delete the list
        todo_list.delete()
        
        # Return success response
        return JsonResponse({
            'success': True,
            'id': pk,
            'message': f'Note "{list_title}" has been deleted successfully.'
        })
        
    except TodoList.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Note not found or you do not have permission to delete it.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)


# Alternative version if you want to handle both POST and DELETE for deletion




@csrf_exempt
@login_required
@require_http_methods(["POST"])
def update_list(request, pk):
    """
    Update list content via AJAX
    """
    try:
        todo_list = get_object_or_404(TodoList, pk=pk, user=request.user)
        
        # Parse JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        
        # Validate and update fields
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        tags = data.get('tags', '').strip()
        quick_notes = data.get('quick_notes', '').strip()
        
        # Validate title (required)
        if not title:
            return JsonResponse({
                'success': False,
                'error': 'Title is required'
            }, status=400)
        
        if len(title) > 200:
            return JsonResponse({
                'success': False,
                'error': 'Title must be less than 200 characters'
            }, status=400)
        
        # Validate description length
        if len(description) > 10000:
            return JsonResponse({
                'success': False,
                'error': 'Description must be less than 10,000 characters'
            }, status=400)
        
        # Update the list
        todo_list.title = title
        todo_list.description = description
        
        # Handle additional fields if they exist in your model
        # If you don't have these fields, you can store them in a JSON field or ignore them
        try:
            # Check if your model has these fields
            if hasattr(todo_list, 'tags'):
                todo_list.tags = tags
            if hasattr(todo_list, 'quick_notes'):
                todo_list.quick_notes = quick_notes
        except AttributeError:
            # These fields don't exist in the model, that's okay
            pass
        
        todo_list.updated_at = timezone.now()
        todo_list.save()
        
        logger.info(f"List {pk} updated by user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Changes saved successfully',
            'updated_at': todo_list.updated_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error updating note {pk}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'An error occurred while saving: {str(e)}'
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def toggle_list_completion(request, pk):
    """
    Toggle the completion status of a todo list
    """
    try:
        todo_list = get_object_or_404(TodoList, pk=pk, user=request.user)
        
        # Toggle completion status
        todo_list.is_completed = not todo_list.is_completed
        todo_list.updated_at = timezone.now()
        todo_list.save()
        
        logger.info(f"Note {pk} completion toggled to {todo_list.is_completed} by user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'completed': todo_list.is_completed,
            'message': f'Note marked as {"completed" if todo_list.is_completed else "active"}!'
        })
        
    except Exception as e:
        logger.error(f"Error toggling completion for note {pk}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)



# whattodo/views.py
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView, 
    PasswordResetCompleteView,
    LoginView,
    
)


import logging
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, 
    PasswordResetConfirmView, PasswordResetCompleteView, LoginView
)

logger = logging.getLogger(__name__)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'whattodo/password_reset.html'
    success_url = reverse_lazy('whattodo:password_reset_done')
    email_template_name = 'whattodo/password_reset_email.html'
    subject_template_name = 'whattodo/password_reset_subject.txt'
    
    def form_valid(self, form):
        logger.info("🔍 Password reset form submitted")
        email = form.cleaned_data.get('email')
        logger.info(f"Email entered: {email}")
        
        # Check if user exists
        users = User.objects.filter(email=email, is_active=True)
        logger.info(f"Active users found with email '{email}': {users.count()}")
        
        if users.exists():
            user = users.first()
            logger.info(f"Sending reset email to user: {user.username} ({user.email})")
        else:
            logger.warning(f"No active user found with email: {email}")
        
        messages.success(self.request, 'If an account with that email exists, a password reset email has been sent.')
        return super().form_valid(form)

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'whattodo/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'whattodo/password_reset_confirm.html'
    success_url = reverse_lazy('whattodo:password_reset_complete')
    
    def form_valid(self, form):
        logger.info("Password successfully changed via reset link")
        messages.success(self.request, 'Your password has been changed successfully.')
        return super().form_valid(form)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'whattodo/password_reset_complete.html'

class CustomLoginView(LoginView):
    template_name = 'whattodo/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('whattodo:dashboard')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


def custom_logout(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('whattodo:login')


from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

@csrf_protect
def logout_view(request):
    if request.method == "POST":
        user_name = request.user.first_name or request.user.username
        logout(request)
        messages.success(request, f'Goodbye, {user_name}! You have been logged out successfully.')
    return redirect('whattodo:login')





