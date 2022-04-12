from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Seat, Flight


@receiver(post_save, sender=Flight)
def create_student_invoice_items(sender, instance, created, **kwargs):
    if created:
        for num in range(1, instance.capacity + 1):
            Seat.objects.create(flight=instance, seat_number=num)
