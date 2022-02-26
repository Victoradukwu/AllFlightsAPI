# Generated by Django 4.0.2 on 2022-02-26 07:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_seat_created_seat_modified_carrier'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='carrier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='flights', to='app.carrier'),
        ),
    ]
