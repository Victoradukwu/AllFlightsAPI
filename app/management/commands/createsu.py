from django.core.management.base import BaseCommand

from app.models import User


class Command(BaseCommand):
    help = 'Creates the first super user'

    def handle(self, *args, **options):
        if not User.objects.filter(email="victordude@allflights.com").exists():
            User.objects.create_superuser("victordude@allflights.com", "abc123")
