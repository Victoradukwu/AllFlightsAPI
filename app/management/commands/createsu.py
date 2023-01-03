from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(email="victor@allflights.com").exists():
            User.objects.create_superuser("victor@allflights.com", "victor@allflights.com", "abc123")
