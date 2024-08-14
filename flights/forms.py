from django import forms
from .models import Flight, Airport, Booking, Payment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from decimal import Decimal

class SearchForm(forms.Form):
    TRIP_CHOICES = (
        ('one_way', 'One Way'),
        ('round_trip', 'Round Trip'),
    )
    trip_type = forms.ChoiceField(choices=TRIP_CHOICES, widget=forms.RadioSelect)
    origin = forms.ModelChoiceField(queryset=Airport.objects.all(), empty_label="Select Origin")
    destination = forms.ModelChoiceField(queryset=Airport.objects.all(), empty_label="Select Destination")
    departure_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    return_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    adults = forms.IntegerField(min_value=1, initial=1)
    children = forms.IntegerField(min_value=0, initial=0)
    infants = forms.IntegerField(min_value=0, initial=0)

class BookingForm(forms.ModelForm):
    adults = forms.DecimalField(min_value=Decimal('1.00'), max_digits=5, decimal_places=2, initial=Decimal('1.00'))
    children = forms.DecimalField(min_value=Decimal('0.00'), max_digits=5, decimal_places=2,
                                      initial=Decimal('0.00'))
    infants = forms.DecimalField(min_value=Decimal('0.00'), max_digits=5, decimal_places=2, initial=Decimal('0.00'))

    class Meta:
        model = Booking
        fields = ['passenger_name', 'email', 'adults', 'children', 'infants', 'ticket_class', 'food_choice']
        widgets = {
            'passenger_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adults': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'children': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'infants': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'ticket_class': forms.Select(attrs={'class': 'form-control'}),
            'food_choice': forms.Select(attrs={'class': 'form-control'}),
        }

class PaymentForm(forms.ModelForm):
    card_number = forms.CharField(min_length=16, max_length=16, widget=forms.TextInput(attrs={'class': 'form-control'}))
    cvv = forms.CharField(min_length=3, max_length=3, widget=forms.TextInput(attrs={'class': 'form-control'}))
    expiry_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta:
        model = Payment
        fields = ['card_number', 'cvv', 'expiry_date']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class FlightForm(forms.ModelForm):
    origin = forms.ModelChoiceField(
        queryset=Airport.objects.all(),
        empty_label="Select Origin",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    destination = forms.ModelChoiceField(
        queryset=Airport.objects.all(),
        empty_label="Select Destination",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Flight
        fields = ['flight_number', 'origin', 'destination', 'departure_time', 'arrival_time',
                  'economy_price', 'business_price', 'available_seats', 'is_international', 'day_of_week']
        widgets = {
            'flight_number': forms.TextInput(attrs={'class': 'form-control'}),
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'economy_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'business_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_international': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
        }