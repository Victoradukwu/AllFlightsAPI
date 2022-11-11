# Generated by Django 4.0.2 on 2022-02-25 22:13

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('departure_time', models.DateTimeField()),
                ('estimated_duration', models.DurationField(help_text='Estimated number of hours in flight')),
                ('fare', models.DecimalField(decimal_places=2, max_digits=6)),
                ('flight_number', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', max_length=8)),
                ('departure_port', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outbound_flights', to='app.airport')),
                ('destination_port', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbound_flights', to='app.airport')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seat_number', models.IntegerField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('Available', 'Available'), ('Booked', 'Booked')], default='Available', max_length=10)),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seats', to='app.flight')),
            ],
            options={
                'unique_together': {('seat_number', 'flight')},
            },
        ),
    ]