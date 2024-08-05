import csv
from django.core.management.base import BaseCommand
from flights.models import Airport, Flight
from flights.management.commands.import_csv_data import Command as ImportCommand
from datetime import datetime

class Command(BaseCommand):
    help = 'Import data from CSV files'

    def handle(self, *args, **options):
        self.import_airports()
        self.import_flights()
        import_command = ImportCommand()
        import_command.handle(self,*args,**options)

    def import_airports(self):
        with open('airports.json', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Airport.objects.get_or_create(
                    code=row['code'],
                    defaults={
                        'name': row['airport'],
                        'city': row['city'],
                        'country': row['country']
                    }
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported airports'))

    def import_flights(self):
        with open('domestic_flights.json', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                origin = Airport.objects.get(code=row['origin'])
                destination = Airport.objects.get(code=row['destination'])
                Flight.objects.get_or_create(
                    flight_number=row['flight_no'],
                    defaults={
                        'origin': origin,
                        'destination': destination,
                        'departure_time': datetime.strptime(f"{row['depart_weekday']} {row['depart_time']}", "%A %H:%M"),
                        'arrival_time': datetime.strptime(f"{row['arrival_weekday']} {row['arrival_time']}", "%A %H:%M"),
                        'price': float(row['economy_fare']),
                        'available_seats': 100
                    }
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported domestic flights'))


        with open('international_flights.json', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                origin = Airport.objects.get(code=row['origin'])
                destination = Airport.objects.get(code=row['destination'])
                Flight.objects.get_or_create(
                    flight_number=row['flight_no'],
                    defaults={
                        'origin': origin,
                        'destination': destination,
                        'departure_time': datetime.strptime(f"{row['depart_weekday']} {row['depart_time']}", "%A %H:%M"),
                        'arrival_time': datetime.strptime(f"{row['arrival_weekday']} {row['arrival_time']}", "%A %H:%M"),
                        'price': float(row['economy_fare']),
                        'available_seats': 100
                    }
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported international flights'))
        self.stdout.write(self.style.s)