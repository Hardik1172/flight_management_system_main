# import_data.py

import csv
import os
import django
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flight_management_system.settings')
django.setup()

from flights.models import Airport, Flight

def import_flights(flights_data, is_international=False):
    reader = csv.DictReader(flights_data.splitlines())
    for row in reader:
        try:
            origin = Airport.objects.get(code=row['origin'])
            destination = Airport.objects.get(code=row['destination'])

            depart_time = make_aware(datetime.strptime(f"2023-01-01 {row['depart_time']}", "%Y-%m-%d %H:%M"))
            duration = timedelta(hours=int(row['duration'].split(':')[0]), minutes=int(row['duration'].split(':')[1]))
            arrival_time = depart_time + duration

            Flight.objects.create(
                flight_number=row['flight_no'],
                origin=origin,
                destination=destination,
                departure_time=depart_time,
                arrival_time=arrival_time,
                price=float(row['economy_fare']),
                economy_price=float(row['economy_fare']),
                business_price=float(row['business_fare']),
                available_seats=100,
                is_international=is_international,
                day_of_week=depart_time.weekday()
            )
        except Airport.DoesNotExist:
            print(f"Skipping flight {row['flight_no']}: Airport not found")
        except Exception as e:
            print(f"Error importing flight {row['flight_no']}: {str(e)}")

    print(f"{'International' if is_international else 'Domestic'} flights imported successfully")

def import_airports():
    airports_data = '''code,name,city,country
DEL,Indira Gandhi International Airport,Delhi,India
BOM,Chhatrapati Shivaji Maharaj International Airport,Mumbai,India
BLR,Kempegowda International Airport,Bangalore,India
MAA,Chennai International Airport,Chennai,India
CCU,Netaji Subhas Chandra Bose International Airport,Kolkata,India
HYD,Rajiv Gandhi International Airport,Hyderabad,India
DXB,Dubai International Airport,Dubai,UAE
SIN,Singapore Changi Airport,Singapore,Singapore
LHR,London Heathrow Airport,London,UK
JFK,John F. Kennedy International Airport,New York,USA'''

    reader = csv.DictReader(airports_data.splitlines())
    for row in reader:
        Airport.objects.get_or_create(
            code=row['code'],
            defaults={
                'name': row['name'],
                'city': row['city']
            }
        )
    print("Airports imported successfully")

# ... rest of the file remains the same

if __name__ == '__main__':
    import_airports()
    # ... rest of the main block remains the same