from django.core.management.base import BaseCommand
from flights.models import Flight


class Command(BaseCommand):
    help = 'Deletes all existing flights'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting all existing flights...')

        # Count the number of flights before deletion
        flights_count = Flight.objects.count()

        # Delete all flights
        Flight.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {flights_count} flights'))