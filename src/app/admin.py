from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin
from .forms import UserCreationForm, UserChangeForm
from .models import User, Seat, Flight, Airport, Carrier, Ticket, PasswordResetToken, FlightClass


@admin.register(User)
class AppUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    filter_horizontal = ['groups', 'user_permissions']

    list_display_links = ('email', 'id')
    list_display = (
        'id',
        'first_name',
        'last_name',
        'phone_number',
        'username',
        'email',
        'country',
    )
    search_fields = (
        'first_name',
        'last_name',
        'email',

    )
    list_filter = ['country']
    ordering = ['email']
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'phone_number',
                    'password1',
                    'password2',
                    'is_staff',
                    'is_active',
                    'is_superuser'
                ),
            },
        ),
    )
    fieldsets = (
                    (
                        None,
                        {
                            'classes': ('wide',),
                            'fields': (
                                'first_name',
                                'last_name',
                                'email',
                                'phone_number',
                                'password',
                                'is_staff',
                                'is_active',
                                'is_superuser',
                                'groups',
                                'user_permissions'
                            )
                        }
                    ),
                )


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = [
        'departure_date',
        'departure_time',
        'departure_port',
        'destination_port',
        'duration',
        'flight_number',
        'status'
    ]
    search_fields = [
        'departure_date',
        'departure_time',
        'departure_port__name',
        'destination_port__name',
        'flight_number',
        'carrier__name'
    ]
    ordering = ["-created"]
    list_filter = ['departure_port', 'destination_port', 'carrier']


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['seat_number', 'flight_class', 'status', 'created', 'modified']
    search_fields = ['seat_number', 'flight_class__class_name', 'status']
    ordering = ["-created"]
    list_filter = ['flight_class', 'flight_class__flight', 'status']


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'country']
    search_fields = ['name', 'code', 'country']
    ordering = ["-created"]
    list_filter = ['country']


@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ['name', 'country']
    search_fields = ['name', 'country__name']
    ordering = ["-created"]
    list_filter = ['country']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'first_name', 'last_name', 'email', 'phone', 'flight', 'seat']
    search_fields = [
        'ticket_number',
        'first_name',
        'last_name',
        'email',
        'phone',
        'seat__flight_class__flight__flight_number'
    ]
    ordering = ["-created"]
    list_filter = ['seat__flight_class__flight']


@admin.register(PasswordResetToken)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['key', 'status', 'user']
    search_fields = ['user__first_name', 'user__last_name', 'key']
    ordering = ["-created"]
    list_filter = ['user']


@admin.register(FlightClass)
class FlightClassAdmin(admin.ModelAdmin):
    list_display = ['flight', 'class_name', 'fare', 'capacity']
    search_fields = ['flight__carrier__name', 'class_name']
    list_filter = ['flight', 'class_name']
