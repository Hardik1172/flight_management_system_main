from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import timedelta


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
    def duration_minutes(self):
        return (self.arrival_time - self.departure_time).total_seconds() / 60

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
    return_flight = models.ForeignKey(Flight, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='return_bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Confirmed')
    seat_number = models.CharField(max_length=5, default='')
    passenger_name = models.CharField(max_length=100)
    email = models.EmailField()
    adults = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'))
    children = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    infants = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    price_before_tax = models.DecimalField(max_digits=5, decimal_places=2)
    ticket_class = models.CharField(max_length=10, choices=TICKET_CLASSES, default='economy')
    food_choice = models.CharField(max_length=10, choices=FOOD_CHOICES, default='veg')

    def total_price(self):
        base_price = self.flight.business_price if self.ticket_class == 'business' else self.flight.economy_price
        adult_price = base_price * self.adults
        child_price = base_price * Decimal('0.7') * self.children
        infant_price = base_price * Decimal('0.5') * self.infants
        self.price_before_tax = adult_price + child_price + infant_price
        total = (adult_price + child_price + infant_price) * Decimal(0.18) + adult_price + child_price +infant_price



        if self.return_flight:
            return_base_price = self.return_flight.business_price if self.ticket_class == 'business' else self.return_flight.economy_price
            return_adult_price = return_base_price * self.adults
            return_child_price = return_base_price * Decimal('0.7') * self.children
            return_infant_price = return_base_price * Decimal('0.5') * self.infants
            self.price_before_tax= adult_price + child_price + infant_price
            total += (return_adult_price + return_child_price + return_infant_price)  * Decimal(0.18) + return_adult_price + return_infant_price + return_child_price


        return total.quantize(Decimal('0.01'))



    def __str__(self):
        return f"Booking {self.id} - {self.user.username} on {self.flight}"




class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)
    expiry_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.id}"