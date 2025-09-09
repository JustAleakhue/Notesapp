from django.apps import AppConfig


class WhattodoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'whattodo'
    verbose_name = "Task Manager"

    def ready(self):   # <-- must be indented inside the class
        import whattodo.signals


