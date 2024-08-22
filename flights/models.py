from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import random
import string


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

    def duration(self):
        duration = self.arrival_time - self.departure_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m"

    @property
    def duration(self):
        duration = self.arrival_time - self.departure_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m"

    def __str__(self):
        return f"{self.flight_number}: {self.origin} to {self.destination}"


class Stopover(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='stopovers')
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)
    arrival_time = models.DateTimeField()
    departure_time = models.DateTimeField()

    def __str__(self):
        return f"Stopover at {self.airport} for {self.flight}"

class Booking(models.Model):
    TICKET_CLASSES = (
        ('economy', 'Economy'),
        ('business', 'Business'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    return_flight = models.ForeignKey(Flight, on_delete=models.SET_NULL, null=True, blank=True, related_name='return_bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Confirmed')
    adults = models.IntegerField(default=0)
    children = models.IntegerField(default=0)
    infants = models.IntegerField(default=0)
    ticket_class = models.CharField(max_length=10, choices=TICKET_CLASSES, default='economy')

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} on {self.flight}"

    def total_price(self):
        base_price = self.flight.business_price if self.ticket_class == 'business' else self.flight.economy_price
        total = base_price * (self.adults + self.children * Decimal('0.7') + self.infants * Decimal('0.5'))

        if self.return_flight:
            return_base_price = self.return_flight.business_price if self.ticket_class == 'business' else self.return_flight.economy_price
            total += return_base_price * (self.adults + self.children * Decimal('0.7') + self.infants * Decimal('0.5'))

        return total.quantize(Decimal('0.01'))

    def get_passengers(self):
        return self.passenger_set.all()


class Passenger(models.Model):
    PASSENGER_TYPES = [
        ('adult', 'Adult'),
        ('child', 'Child'),
        ('infant', 'Infant'),
    ]
    MEAL_CHOICES = [
        ('Non-Veg', 'Non-Vegetarian'),
        ('vegetarian', 'Vegetarian')
    ]
    TICKET_CLASSES = (
        ('economy', 'Economy'),
        ('business', 'Business'),
    )

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    passenger_type = models.CharField(max_length=10, choices=PASSENGER_TYPES)
    meal_choice = models.CharField(max_length=20, choices=MEAL_CHOICES, default='vegetarian')
    seat_number = models.CharField(max_length=5, null=True, blank=True)
    passenger_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    ticket_class = models.CharField(max_length=10, choices=TICKET_CLASSES, default='economy')

    def save(self, *args, **kwargs):
        if not self.passenger_id:
            self.passenger_id = self.generate_passenger_id()
        super().save(*args, **kwargs)

    def generate_passenger_id(self):
        prefix = self.passenger_type[0].upper()
        while True:
            passenger_id = f"{prefix}{random.randint(100000, 999999)}"
            if not Passenger.objects.filter(passenger_id=passenger_id).exists():
                return passenger_id

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_passenger_type_display()})"
class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)
    expiry_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.id}"

class Passenger(models.Model):
    PASSENGER_TYPES = [
        ('adult', 'Adult'),
        ('child', 'Child'),
        ('infant', 'Infant'),
    ]
    MEAL_CHOICES = [
        ('Non-Veg', 'Non-Vegetarian'),
        ('vegetarian', 'Vegetarian')
    ]
    TICKET_CLASSES = (
        ('economy', 'Economy'),
        ('business', 'Business'),
    )

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    passenger_type = models.CharField(max_length=10, choices=PASSENGER_TYPES)
    meal_choice = models.CharField(max_length=20, choices=MEAL_CHOICES, default='vegetarian')
    seat_number = models.CharField(max_length=5, null=True, blank=True)
    passenger_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    ticket_class = models.CharField(max_length=10, choices=TICKET_CLASSES, default='economy')

    def save(self, *args, **kwargs):
        if not self.passenger_id:
            self.passenger_id = self.generate_passenger_id()
        super().save(*args, **kwargs)

    def generate_passenger_id(self):
        prefix = self.passenger_type[0].upper()
        while True:
            passenger_id = f"{prefix}{random.randint(100000, 999999)}"
            if not Passenger.objects.filter(passenger_id=passenger_id).exists():
                return passenger_id

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_passenger_type_display()})"


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    origin = models.ForeignKey(Airport, on_delete=models.SET_NULL, null=True, related_name='search_origins')
    destination = models.ForeignKey(Airport, on_delete=models.SET_NULL, null=True, related_name='search_destinations')
    departure_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)
    infants = models.IntegerField(default=0)
    search_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-search_date']

    def __str__(self):
        return f"{self.user.username} - {self.origin} to {self.destination}"