# Generated by Django 3.2.13 on 2022-05-22 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_auto_20220522_1832'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flight',
            name='business_capacity',
        ),
        migrations.RemoveField(
            model_name='flight',
            name='economy_capacity',
        ),
        migrations.RemoveField(
            model_name='flight',
            name='premium_capacity',
        ),
        migrations.AddField(
            model_name='flightclass',
            name='capacity',
            field=models.IntegerField(default=1),
        ),
    ]