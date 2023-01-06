from django.core.management.base import BaseCommand

from app.models import User


class Command(BaseCommand):
    help = 'Creates the first super user'

    def handle(self, *args, **options):
        if not User.objects.filter(email="johnny@allflights.com").exists():
            User.objects.create_superuser("johnny@allflights.com", "abc123")
