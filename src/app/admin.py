from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin
from .forms import UserCreationForm, UserChangeForm
from .models import User, Seat, Flight, Airport, Carrier, Ticket, PasswordResetToken


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
        'fare',
        'flight_number',
        'status',
        'capacity'
    ]
    search_fields = ['departure_date', 'departure_time', 'departure_port', 'destination_port', 'flight_number']
    ordering = ["-created"]
    list_filter = ['departure_port', 'destination_port']


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['seat_number', 'flight', 'status']
    search_fields = ['seat_number', 'flight', 'status']
    ordering = ["-created"]
    list_filter = ['flight', 'status']


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'country']
    search_fields = ['name', 'code', 'country']
    ordering = ["-created"]
    list_filter = ['country']


@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ['name', 'country']
    search_fields = ['name', 'country']
    ordering = ["-created"]
    list_filter = ['country']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'first_name', 'last_name', 'email', 'phone', 'flight', 'seat']
    search_fields = ['ticket_number', 'first_name', 'last_name', 'email', 'phone', 'flight', 'seat']
    ordering = ["-created"]
    list_filter = ['flight']


@admin.register(PasswordResetToken)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['key', 'status', 'user']
    search_fields = ['user__first_name', 'user__last_name', 'key']
    ordering = ["-created"]
    list_filter = ['user']
