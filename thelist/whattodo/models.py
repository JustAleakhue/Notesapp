from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class TodoList(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_lists')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Todo List'
        verbose_name_plural = 'Todo Lists'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('whattodo:list_detail', kwargs={'pk': self.pk})
    
    @property
    def total_tasks(self):
        return self.tasks.count()
    
    @property
    def completed_tasks(self):
        return self.tasks.filter(is_completed=True).count()
    
    @property
    def completion_percentage(self):
        if self.total_tasks == 0:
            return 0
        return (self.completed_tasks / self.total_tasks) * 100

class Task(models.Model):
    todo_list = models.ForeignKey(TodoList, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['is_completed', 'created_at'],
        models.Index(fields=['user', '-updated_at']),

    
    def __str__(self):
        return f"{self.title} ({'✓' if self.is_completed else '○'})"



from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s Profile"
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
