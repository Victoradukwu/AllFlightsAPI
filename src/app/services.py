from . import models
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
