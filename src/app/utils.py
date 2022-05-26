from celery import shared_task
from django.core.mail import EmailMessage
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.response import Response

from . import models


@shared_task
def send_email(payload):
    subject = payload['subject']
    html_content = payload['html_content']
    to_email = payload['to_email'],
    email = EmailMessage(subject, html_content, to=to_email)
    email.content_subtype = "html"
    email.send()


def custom_exception_handler(exc, context):

    msg = exc.detail if hasattr(exc, 'detail') else str(exc)
    return Response({'detail': msg}, status=status.HTTP_400_BAD_REQUEST)

def generate_flight_number(departure_port):
    last_flight = departure_port.outbound_flights.order_by("-id").first()
    if last_flight:
        last_number = int(last_flight.flight_number[3:])
    else:
        last_number = 0

    return f"{departure_port.code}{last_number+1}"


def generate_ticket_number(flight):
    last_ticket = flight.tickets.order_by("-id").first()
    if last_ticket:
        last_number = int(last_ticket.split('-')[-1])
    else:
        last_number = 0

    return f"{flight.flight_number}-{last_number+1}"


def generate_seat_number(seat):
    last_seat = models.Seat.objects.filter(flight_class__flight=seat.flight_class.flight).order_by("-created").first()
    if last_seat:
        last_number = int(last_seat.seat_number.split("-")[-1])
    else:
        last_number = 0
    return f"{seat.flight_class.flight.flight_number}-{last_number + 1}"


class FlightFilter(filters.FilterSet):
    destination = filters.CharFilter(field_name='destination_port__name', lookup_expr='icontains')
    departure = filters.CharFilter(field_name='departure_port__name', lookup_expr='icontains')
    departureDate = filters.LookupChoiceFilter(field_name='departure_date', lookup_choices=[('exact', 'On'), ('gte', 'After'), ('lte', 'Before')])

