from datetime import date, timedelta
import os

from celery import shared_task
from django.core.mail import EmailMessage
from django_filters import rest_framework as filters
import requests
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from . import models


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


def generate_ticket_number(seat):
    last_ticket = models.Ticket.objects.filter(
        seat__flight_class__flight=seat.flight_class.flight
    ).order_by("-id").first()
    if last_ticket:
        last_number = int(last_ticket.ticket_number.split('-')[-1])
    else:
        last_number = 0

    return f"{seat.flight_class.flight.flight_number}-{last_number+1}"


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
    departureDate = filters.LookupChoiceFilter(
        field_name='departure_date',
        lookup_choices=[('exact', 'On'), ('gte', 'After'), ('lte', 'Before')]
    )


def make_payment(payload):
    test_secret = os.getenv('PAYSTACK_SECRET_KEY')
    headers = {'Authorization': f'Bearer {test_secret}'}
    resp = requests.post('https://api.paystack.co/charge', json=payload, headers=headers)
    return resp.json()


@shared_task
def send_email(payload):
    subject = payload['subject']
    html_content = payload['html_content']
    to_email = payload['to_email'],
    email = EmailMessage(subject, html_content, to=to_email)
    email.content_subtype = "html"
    email.send()


def send_reminders():
    """Send reminders to traveller who are travelling the next day"""
    next_day = date.today() + timedelta(days=1)
    tickets = models.Ticket.objects.filter(seat__flight__departure_time__date=next_day)
    for ticket in tickets:
        email_body = f'<html>' \
                     f'<head>' \
                     f'</head>' \
                     f'<body>' \
                     f'<p>Hi {ticket.first_name},</p>' \
                     f'<p>Please be reminded of your schedulled flight as follows:</p>' \
                     f'<p>' \
                     f'Name: {ticket.first_name} {ticket.last_name}<br>' \
                     f'Date: {ticket.seat.flight_class.flight.departure_dater}<br>' \
                     f'Time: {ticket.seat.flight_class.flight.departure_timer}<br>'\
                     f'Flight Number: {ticket.seat.flight_class.flight.flight_number}<br>' \
                     f'Seat Number: {ticket.seat.seat_number}<br>' \
                     f'Ticket Number: {ticket.ticket_number}<br>' \
                     f'Carrier: {ticket.seat.flight_class.flight.carrier.name}<br>' \
                     f'</p>' \
                     f'<p>' \
                     f'Thank you, <br>' \
                     f'The <b>Allflights</b> team' \
                     f'</p>'\
                     f'</body>' \
                     f'</html>'
        payload = {
            'subject': 'Travel Reminder',
            'html_content': email_body,
            'to_email': ticket.email
        }
        send_email.delay(payload)


class IsAdminOrCreateOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_staff) or request.method == 'POST'


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method == 'GET' or (request.user.is_authenticated and request.user.is_staff)
