# Generated by Django 4.0.2 on 2022-02-27 14:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_flight_flight_number_ticket'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='departure_date',
            field=models.DateField(default=datetime.date(2022, 2, 27)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='flight',
            name='departure_time',
            field=models.TimeField(),
        ),
    ]
