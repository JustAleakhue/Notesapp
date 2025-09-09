from django.contrib import admin
from .models import TodoList, Task

@admin.register(TodoList)
class TodoListAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'is_completed', 'created_at', 'task_count', 'completion_percentage']
    list_filter = ['is_completed', 'created_at', 'user']
    search_fields = ['title', 'description', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_completed']

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'user')
        }),
        ('Additional', {
            'fields': ('tags', 'quick_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def task_count(self, obj):
        return obj.total_tasks
    task_count.short_description = 'Total Tasks'
    
    def completion_percentage(self, obj):
        return f"{obj.completion_percentage:.1f}%"
    completion_percentage.short_description = 'Progress'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'todo_list', 'list_owner', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'created_at', 'todo_list__user']
    search_fields = ['title', 'description', 'todo_list__title', 'todo_list__user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def list_owner(self, obj):
        return obj.todo_list.user.username
    list_owner.short_description = 'Owner'