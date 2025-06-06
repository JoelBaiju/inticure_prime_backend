# Generated by Django 5.2.1 on 2025-06-01 09:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0005_alter_appointmentquestionsandanswers_appointment_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointmentheader',
            old_name='appointment_time_slot_id',
            new_name='appointment_slot',
        ),
        migrations.RemoveField(
            model_name='appointmentheader',
            name='category_id',
        ),
        migrations.RemoveField(
            model_name='appointmentheader',
            name='user_id',
        ),
        migrations.AddField(
            model_name='appointmentheader',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_header', to='analysis.category'),
        ),
        migrations.AddField(
            model_name='appointmentheader',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_header', to=settings.AUTH_USER_MODEL),
        ),
    ]
