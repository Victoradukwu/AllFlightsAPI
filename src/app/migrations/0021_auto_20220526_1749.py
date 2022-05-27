# Generated by Django 3.2.13 on 2022-05-26 16:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20220522_2215'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='flight',
        ),
        migrations.AddField(
            model_name='airport',
            name='city',
            field=models.CharField(default='Lagos', max_length=20),
        ),
        migrations.AddField(
            model_name='ticket',
            name='contact_first_name',
            field=models.CharField(default='Victor', max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticket',
            name='contact_last_name',
            field=models.CharField(default='Duke', max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticket',
            name='gender',
            field=models.CharField(default='Male', max_length=7),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='flightclass',
            name='flight',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='app.flight'),
        ),
    ]
