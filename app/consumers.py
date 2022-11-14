
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.decorators import action

from .serializers import FlightSerializer
from .models import Flight, Seat


class TicketBookedConsumer(GenericAsyncAPIConsumer):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    @model_observer(Seat)
    async def ticket_booking(self, message: FlightSerializer, action, **kwargs):
        if action == 'update':
            await self.send_json(dict(message))

    @ticket_booking.serializer
    def ticket_booking(self, instance: Seat, action, **kwargs) -> FlightSerializer:
        """This will return the flight serializer"""
        return FlightSerializer(instance.flight_class.flight).data

    @action()
    async def subscribe_to_ticket_booking(self, request_id, **kwargs):
        await self.ticket_booking.subscribe(request_id=request_id)

