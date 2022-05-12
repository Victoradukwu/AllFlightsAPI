import os
import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group
from django.db import models
from django_extensions.db.models import TimeStampedModel
from versatileimagefield.fields import VersatileImageField
from . import services


def path_and_filename(instance, filename):
    upload_to = f'medias/{instance.__class__.__name__.lower()}'
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return os.path.join(upload_to, filename)  # TODO change to use the Path module from standard library


class Country(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    iso_3166 = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.id}: {self.name}'


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.groups.add(Group.objects.get(name='admin'))
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):

    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    avatar = VersatileImageField('guardian_avatar', null=True, blank=True, upload_to=path_and_filename)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def has_perm(self, perm, obj=None):
        """
        Check if the user has a specific permission
        """
        return True

    def has_module_perms(self, app_label):
        """
        Check if a user has permissions to view the app `app_label`
        """
        return True

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class Airport(TimeStampedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='airports')

    def __str__(self):
        return f'{self.country}: {self.name}'


class Carrier(TimeStampedModel):

    name = models.CharField(max_length=100)
    country = models.ForeignKey('Country', related_name='carriers', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.country}: {self.name}'


class Flight(TimeStampedModel):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    STATUS_CHOICES = [(ACTIVE, ACTIVE), (INACTIVE, INACTIVE)]

    departure_time = models.TimeField()
    departure_date = models.DateField()
    departure_port = models.ForeignKey('Airport', related_name='outbound_flights', on_delete=models.CASCADE)
    destination_port = models.ForeignKey('Airport', related_name='inbound_flights', on_delete=models.CASCADE)
    duration = models.DurationField(help_text='Estimated duration of flight', null=True)
    fare = models.DecimalField(max_digits=6, decimal_places=2)
    flight_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=ACTIVE)
    capacity = models.IntegerField()
    carrier = models.ForeignKey('Carrier', related_name='flights', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.flight_number}: {self.departure_port.code}_{self.destination_port.code}'

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.flight_number = services.generate_flight_number(self.departure_port)

        super().save(*args, **kwargs)

    class Meta:
        unique_together = (('flight_number', 'departure_port'),)


class Seat(TimeStampedModel):
    """A model class representing a particular seat on a particular flight"""
    AVAILABLE = 'Available'
    BOOKED = 'Booked'
    STATUS_CHOICES = [(AVAILABLE, AVAILABLE), (BOOKED, BOOKED)]

    seat_number = models.IntegerField()
    flight = models.ForeignKey(Flight, related_name='seats', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=AVAILABLE)

    def __str__(self):
        return f'{self.flight.flight_number}: {self.seat_number}'

    class Meta:
        unique_together = (('seat_number', 'flight'),)


class Ticket(TimeStampedModel):
    """A model class representing a passenger ticket"""

    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    ticket_number = models.CharField(max_length=10, null=True, blank=True, unique=True)
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE, related_name='tickets')

    def __str__(self):
        return f'{self.seat.flight.flight_number}: {self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.ticket_number = services.generate_ticket_number(self.flight)

        super().save(*args, **kwargs)


class PasswordResetToken(TimeStampedModel):
    key = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
