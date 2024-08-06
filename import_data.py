import csv
import os
import django
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flight_management_system.settings')
django.setup()

from flights.models import Airport, Flight

def import_airports():
    airports_data = '''code,name,city,country
JFK,John F. Kennedy International Airport,New York,USA
LHR,London Heathrow Airport,London,UK
CDG,Charles de Gaulle Airport,Paris,France
DXB,Dubai International Airport,Dubai,UAE
SIN,Singapore Changi Airport,Singapore,Singapore
LAX,Los Angeles International Airport,Los Angeles,USA
ORD,O'Hare International Airport,Chicago,USA
HND,Tokyo Haneda Airport,Tokyo,Japan
FRA,Frankfurt Airport,Frankfurt,Germany
SYD,Sydney Airport,Sydney,Australia
ATL,Hartsfield-Jackson Atlanta International Airport,Atlanta,USA
DFW,Dallas/Fort Worth International Airport,Dallas,USA
SFO,San Francisco International Airport,San Francisco,USA
SEA,Seattle-Tacoma International Airport,Seattle,USA
DEN,Denver International Airport,Denver,USA
NRT,Narita International Airport,Tokyo,Japan'''

    reader = csv.DictReader(airports_data.splitlines())
    for row in reader:
        Airport.objects.get_or_create(
            code=row['code'],
            defaults= {
                'name' : row['name'],
                'city' : row['city'],
                'country' : row['country']
            }
        )
    print("Airports imported successfully")

def import_flights(flights_data, is_international=False):
    reader = csv.DictReader(flights_data.splitlines())
    for row in reader:
        try:
            origin = Airport.objects.get(code=row['origin'])
            destination = Airport.objects.get(code=row['destination'])

            # Calculate departure and arrival times
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
                available_seats=100,
                is_international=is_international
            )
        except Airport.DoesNotExist:
            print(f"Skipping flight {row['flight_no']}: Airport not found")
        except Exception as e:
            print(f"Error importing flight {row['flight_no']}: {str(e)}")

    print(f"{'International' if is_international else 'Domestic'} flights imported successfully")

if __name__ == '__main__':
    # Import airports
    import_airports()

    # Import domestic flights
    domestic_flights_data = '''origin,destination,depart_time,depart_weekday,duration,arrival_time,arrival_weekday,flight_no,airline_code,airline,economy_fare,business_fare,first_fare
JFK,LAX,08:00,Monday,06:00,14:00,Monday,DL123,DL,Delta Airlines,250.00,500.00,750.00
ORD,ATL,10:30,Tuesday,02:15,12:45,Tuesday,UA456,UA,United Airlines,180.00,350.00,550.00
DFW,SFO,14:45,Wednesday,04:30,19:15,Wednesday,AA789,AA,American Airlines,220.00,450.00,680.00
LAX,JFK,07:00,Thursday,05:30,15:30,Thursday,B6101,B6,JetBlue,280.00,550.00,800.00
SEA,DEN,11:15,Friday,02:45,14:00,Friday,AS234,AS,Alaska Airlines,190.00,380.00,600.00'''
    import_flights(domestic_flights_data)

    # Import international flights
    international_flights_data = '''origin,destination,depart_time,depart_weekday,duration,arrival_time,arrival_weekday,flight_no,airline_code,airline,economy_fare,business_fare,first_fare
JFK,LHR,22:00,Friday,07:00,10:00,Saturday,BA001,BA,British Airways,500.00,1500.00,3000.00
CDG,DXB,14:30,Saturday,06:30,23:00,Saturday,AF002,AF,Air France,600.00,1800.00,3500.00
SIN,SYD,09:15,Sunday,08:00,20:15,Sunday,SQ003,SQ,Singapore Airlines,450.00,1300.00,2800.00
LAX,NRT,11:45,Monday,11:30,15:15,Tuesday,NH004,NH,All Nippon Airways,700.00,2000.00,4000.00
FRA,JFK,13:00,Wednesday,08:30,16:30,Wednesday,LH005,LH,Lufthansa,550.00,1600.00,3200.00'''
    import_flights(international_flights_data, is_international=True)