from django.urls import re_path

from app.consumers import TicketBookedConsumer

websocket_urlpatterns = [re_path(r"ws/ticket-booked/$", TicketBookedConsumer.as_asgi())]
