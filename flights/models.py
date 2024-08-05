from django.db import models
from django.contrib.auth.models import User

class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Flight(models.Model):
    flight_number = models.CharField(max_length=10)
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures')
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.flight_number}: {self.origin} to {self.destination}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Confirmed')
    seat_number = models.CharField(max_length=5)

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} on {self.flight}"