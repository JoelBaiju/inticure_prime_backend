# Generated by Django 5.2.1 on 2025-06-11 07:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0004_countries_delete_locations'),
    ]

    operations = [
        migrations.RenameField(
            model_name='countries',
            old_name='location',
            new_name='country_name',
        ),
    ]
