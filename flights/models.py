# flights/models.py

from django.db import models
from django.contrib.auth.models import User

class Airport(models.Model):
    city = models.CharField(max_length=100)
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.city} ({self.code})"

class Flight(models.Model):
    flight_number = models.CharField(max_length=10)
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures')
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    economy_price = models.DecimalField(max_digits=10, decimal_places=2)
    business_price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.IntegerField(default=100)
    is_international = models.BooleanField(default=False)
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ])


    def save(self, *args, **kwargs):
        self.day_of_week = self.departure_time.weekday()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.flight_number}: {self.origin} to {self.destination}"









class Booking(models.Model):
    TICKET_CLASSES = (
        ('economy', 'Economy'),
        ('business', 'Business'),
    )
    FOOD_CHOICES = (
        ('veg', 'Vegetarian'),
        ('non_veg', 'Non-Vegetarian'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Confirmed')
    seat_number = models.CharField(max_length=5, default='')
    passenger_name = models.CharField(max_length=100)
    email = models.EmailField()
    age = models.IntegerField()
    ticket_class = models.CharField(max_length=10, choices=TICKET_CLASSES, default='economy')
    food_choice = models.CharField(max_length=10, choices=FOOD_CHOICES, default='veg')
    seats = models.IntegerField()

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} on {self.flight}"

    def total_price(self):
        base_price = self.flight.business_price if self.ticket_class == 'business' else self.flight.economy_price
        food_price = 10 if self.food_choice == 'non_veg' else 5
        return (base_price + food_price) * self.seats
    
class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)
    expiry_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.id}"