# Generated by Django 3.2.13 on 2022-05-22 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_auto_20220522_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seat',
            name='seat_number',
            field=models.CharField(max_length=20),
        ),
    ]
