# Generated by Django 4.0.2 on 2022-02-25 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_flight_seat'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seat',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='seat',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='flight',
            name='capacity',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
    ]