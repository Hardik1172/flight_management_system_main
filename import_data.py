# import_data.py

import csv
import os
import django
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flight_management_system.settings')
django.setup()

from flights.models import Airport, Flight


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


if __name__ == '__main__':
    import_airports()

    # You can add your flight data here as a multi-line string
    domestic_flights_data = '''flight_no,origin,destination,depart_time,duration,economy_fare,business_fare
AI101,DEL,BOM,10:00,02:30,5000,10000
AI102,BOM,DEL,13:00,02:30,5500,11000
AI201,DEL,BLR,11:30,03:00,6000,12000
AI202,BLR,DEL,15:00,03:00,6500,13000'''

    international_flights_data = '''flight_no,origin,destination,depart_time,duration,economy_fare,business_fare
AI301,DEL,DXB,22:00,04:00,15000,30000
AI302,DXB,DEL,03:00,04:00,16000,32000
AI401,BOM,LHR,01:30,09:00,40000,80000
AI402,LHR,BOM,11:00,09:00,42000,84000'''

    import_flights(domestic_flights_data, is_international=False)
    import_flights(international_flights_data, is_international=True)