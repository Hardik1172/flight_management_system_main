from django.db import models
from django.contrib.auth.models import User

class Flight(models.Model):
    flight_number = models.CharField(max_length=20, unique=True)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    date = models.DateField()
    available_seats = models.IntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.flight_number}: {self.source} to {self.destination}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=4)
    booking_date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.flight.flight_number}"