# Generated by Django 5.0.6 on 2024-07-24 16:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capstone', '0007_remove_customuser_product_id_meter_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='meters',
            field=models.ManyToManyField(blank=True, related_name='assigned_users', to='capstone.meter'),
        ),
        migrations.AlterField(
            model_name='meter',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='meter_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
