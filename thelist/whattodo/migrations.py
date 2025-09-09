# whattodo/migrations/0005_remove_priority_due_date_fields.py

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('whattodo', '0004_make_fields_nullable'),
    ]

    operations = [
        # Remove priority and due_date fields
        migrations.RemoveField(
            model_name='todolist',
            name='priority',
        ),
        migrations.RemoveField(
            model_name='todolist',
            name='due_date',
        ),
        migrations.RemoveField(
            model_name='task',
            name='priority',
        ),
        migrations.RemoveField(
            model_name='task',
            name='due_date',
        ),
    ]