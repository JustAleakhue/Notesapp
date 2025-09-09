from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = 'whattodo'

urlpatterns = [
    # Home and authentication
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('my-lists/', views.my_lists_view, name='my_lists'),


    
     path('password-reset/', 
         auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt'
         ), 
         name='password_reset'),
    
     path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
     path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
            template_name='whattodo/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
     path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # TodoList CRUD operations
    path('lists/create/', views.create_list_view, name='create_list'),
    path('lists/<int:pk>/', views.list_detail_view, name='list_detail'),
    path('lists/<int:pk>/edit/', views.edit_list_view, name='edit_list'),
    path('lists/<int:pk>/delete/', views.delete_list_view, name='delete_list'),
    path('lists/<int:pk>/toggle/', views.toggle_list_completion, name='toggle_list_completion'),
    path('delete-list/<int:pk>/', views.delete_list, name='delete_list'),
    path('toggle-list-completion/<int:pk>/', views.toggle_list_completion, name='toggle_list_completion'),
    path('update-list/<int:pk>/', views.update_list, name='update_list'),

]
