# Generated by Django 5.0.6 on 2024-07-24 16:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capstone', '0006_remove_meter_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='product_id',
        ),
        migrations.AddField(
            model_name='meter',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='meters', to=settings.AUTH_USER_MODEL),
        ),
    ]