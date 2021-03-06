# Generated by Django 4.0.2 on 2022-02-26 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_flight_carrier'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flight',
            name='estimated_duration',
        ),
        migrations.AddField(
            model_name='flight',
            name='duration',
            field=models.FloatField(default=1, help_text='Estimated number of hours in flight'),
            preserve_default=False,
        ),
    ]
